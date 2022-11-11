load("github.com/kurtosis-tech/eth2-module/src/shared_utils/shared_utils.star", "new_port_spec", "path_join", "path_dir")
load("github.com/kurtosis-tech/eth2-module/src/module_io/parse_input.star", "get_client_log_level_or_default")
load("github.com/kurtosis-tech/eth2-module/src/participant_network/cl/cl_client_context.star", "new_cl_client_context")
load("github.com/kurtosis-tech/eth2-module/src/participant_network/cl/cl_node_metrics_info.star", "new_cl_node_metrics_info")
load("github.com/kurtosis-tech/eth2-module/src/participant_network/mev_boost/mev_boost_context.star", "mev_boost_endpoint")

module_io = import_types("github.com/kurtosis-tech/eth2-module/types.proto")

IMAGE_SEPARATOR_DELIMITER = ","
EXPECTED_NUM_IMAGES       = 2

CONSENSUS_DATA_DIRPATH_ON_SERVICE_CONTAINER      = "/consensus-data"
GENESIS_DATA_MOUNT_DIRPATH_ON_SERVICE_CONTAINER   = "/genesis"
VALIDATOR_KEYS_MOUNT_DIRPATH_ON_SERVICE_CONTAINER = "/validator-keys"
PRYSM_PASSWORD_MOUNT_DIRPATH_ON_SERVICE_CONTAINER = "/prysm-password"

# Port IDs
TCP_DISCOVERY_PORT_ID        = "tcp-discovery"
UDP_DISCOVERY_PORT_ID        = "udp-discovery"
RPC_PORT_ID                 = "rpc"
HTTP_PORT_ID                = "http"
BEACON_MONITORING_PORT_ID    = "monitoring"
VALIDATOR_MONITORING_PORT_ID = "monitoring"

# Port nums
DISCOVERY_TCP_PORT_NUM         = 13000
DISCOVERY_UDP_PORT_NUM         = 12000
RPC_PORT_NUM                  = 4000
HTTP_PORT_NUM                 = 3500
BEACON_MONITORING_PORT_NUM     = 8080
VALIDATOR_MONITORING_PORT_NUM  = 8081

MAX_NUM_HEALTHCHECK_RETRIES      = 100
TIME_BETWEEN_HEALTHCHECK_RETRIES = 5 * time.second

BEACON_SUFFIX_SERVICE_ID    = "beacon"
VALIDATOR_SUFFIX_SERVICE_ID = "validator"

MIN_PEERS = 1

METRICS_PATH = "/metrics"

PRIVATE_IP_ADDRESS_PLACEHOLDER = "KURTOSIS_IP_ADDR_PLACEHOLDER"

# TODO push this into shared_utils
TCP_PROTOCOL = "TCP"
UDP_PROTOCOL = "UDP"

BEACON_NODE_USED_PORTS = {
	TCP_DISCOVERY_PORT_ID:     new_port_spec(DISCOVERY_TCP_PORT_NUM, TCP_PROTOCOL),
	UDP_DISCOVERY_PORT_ID:     new_port_spec(DISCOVERY_UDP_PORT_NUM, UDP_PROTOCOL),
	RPC_PORT_ID:              new_port_spec(RPC_PORT_NUM, TCP_PROTOCOL),
	HTTP_PORT_ID:             new_port_spec(HTTP_PORT_NUM, TCP_PROTOCOL),
	BEACON_MONITORING_PORT_ID: new_port_spec(BEACON_MONITORING_PORT_NUM, TCP_PROTOCOL),
}

VALIDATOR_NODE_USED_PORTS = {
	VALIDATOR_MONITORING_PORT_ID: new_port_spec(VALIDATOR_MONITORING_PORT_NUM, TCP_PROTOCOL),
}

PRYSM_LOG_LEVELS = {
	module_io.GlobalClientLogLevel.error: "error",
	module_io.GlobalClientLogLevel.warn:  "warn",
	module_io.GlobalClientLogLevel.info:  "info",
	module_io.GlobalClientLogLevel.debug: "debug",
	module_io.GlobalClientLogLevel.trace: "trace",
}

BEACON_ENR_FACT_NAME = "beacon-enr-fact"
BEACON_HEALTH_FACT_NAME = "beacon-health-fact"


def launch(
	launcher,
	service_id,
	images,
	participant_log_level,
	global_log_level,
	bootnode_context,
	el_client_context,
	mev_boost_context,
	node_keystore_files,
	extra_beacon_params,
	extra_validator_params):

	split_images = images.split(IMAGE_SEPARATOR_DELIMITER)
	if len(split_images) != EXPECTED_NUM_IMAGES:
		fail("Expected {0} images but got {1}".format(EXPECTED_NUM_IMAGES, len(split_images)))
	beacon_image, validator_image = split_images

	if beacon_image.strip() == "":
		fail("An empty beacon image was provided")

	if validator_image.strip() == "":
		fail("An empty validator image was provided")


	beacon_node_service_id = "{0}-{1}".format(service_id, BEACON_SUFFIX_SERVICE_ID)
	validator_node_service_id = "{0}-{1}".format(service_id, VALIDATOR_SUFFIX_SERVICE_ID)

	log_level = get_client_log_level_or_default(participant_log_level, global_log_level, PRYSM_LOG_LEVELS)

	beacon_service_config = get_beacon_service_config(
		launcher.genesis_data,
		beacon_image,
		bootnode_context,
		el_client_context,
		mev_boost_context,
		log_level,
		extra_beacon_params,
	)

	beacon_service = add_service(beacon_node_service_id, beacon_service_config)

	# TODO the Golang code checks whether its 200, 206 or 503, maybe add that
	# TODO this fact might start breaking if the endpoint requires a leading slash, currently breaks with a leading slash
	define_fact(service_id = beacon_node_service_id, fact_name = BEACON_HEALTH_FACT_NAME, fact_recipe = struct(method= "GET", endpoint = "eth/v1/node/health", content_type = "application/json", port_id = HTTP_PORT_ID))
	wait(service_id = beacon_node_service_id, fact_name = BEACON_HEALTH_FACT_NAME)

	beacon_http_port = beacon_service.ports[HTTP_PORT_ID]

	# Launch validator node
	beacon_http_endpoint = "http://{0}:{1}".format(beacon_service.ip_address, HTTP_PORT_NUM)
	beacon_rpc_endpoint = "http://{0}:{1}".format(beacon_service.ip_address, RPC_PORT_NUM)

	validator_service_config = get_validator_service_config(
		launcher.genesis_data,
		validator_image,
		validator_node_service_id,
		log_level,
		beacon_rpc_endpoint,
		beacon_http_endpoint,
		node_keystore_files,
		mev_boost_context,
		extra_validator_params,
		launcher.prysm_password_relative_filepath,
		launcher.prysm_password_artifact_uuid
	)

	validator_service = add_service(validator_node_service_id, validator_service_config)

	# TODO add validator availability using the validator API: https://ethereum.github.io/beacon-APIs/?urls.primaryName=v1#/ValidatorRequiredApi | from eth2-merge-kurtosis-module
	# TODO this fact might start breaking if the endpoint requires a leading slash, currently breaks with a leading slash
	define_fact(service_id = beacon_node_service_id, fact_name = BEACON_ENR_FACT_NAME, fact_recipe = struct(method= "GET", endpoint = "eth/v1/node/identity", field_extractor = ".data.enr", content_type = "application/json", port_id = HTTP_PORT_ID))
	beacon_node_enr = wait(service_id = beacon_node_service_id, fact_name = BEACON_ENR_FACT_NAME)

	beacon_metrics_port = beacon_service.ports[BEACON_MONITORING_PORT_ID]
	beacon_metrics_url = "{0}:{1}".format(beacon_service.ip_address, beacon_metrics_port.number)

	validator_metrics_port = validator_service.ports[VALIDATOR_MONITORING_PORT_ID]
	validator_metrics_url = "{0}:{1}".format(validator_service.ip_address, validator_metrics_port.number)

	beacon_node_metrics_info = new_cl_node_metrics_info(beacon_node_service_id, METRICS_PATH, beacon_metrics_url)
	validator_node_metrics_info = new_cl_node_metrics_info(validator_node_service_id, METRICS_PATH, validator_metrics_url)
	nodes_metrics_info = [beacon_node_metrics_info, validator_node_metrics_info]


	result = new_cl_client_context(
		"prysm",
		beacon_node_enr,
		beacon_service.ip_address,
		HTTP_PORT_NUM,
		nodes_metrics_info,
		beacon_node_service_id
	)

	return result


def get_beacon_service_config(
		genesis_data,
		beacon_image,
		bootnode_context,
		el_client_context,
		mev_boost_context,
		log_level,
		extra_params,
	):

	el_client_engine_rpc_url_str = "http://{0}:{1}".format(
		el_client_context.ip_addr,
		el_client_context.engine_rpc_port_num,
	)

	genesis_config_filepath = path_join(GENESIS_DATA_MOUNT_DIRPATH_ON_SERVICE_CONTAINER, genesis_data.config_yml_rel_filepath)
	genesis_ssz_filepath = path_join(GENESIS_DATA_MOUNT_DIRPATH_ON_SERVICE_CONTAINER, genesis_data.genesis_ssz_rel_filepath)
	jwt_secret_filepath = path_join(GENESIS_DATA_MOUNT_DIRPATH_ON_SERVICE_CONTAINER, genesis_data.jwt_secret_rel_filepath)


	cmd_args = [
		"--accept-terms-of-use=true", #it's mandatory in order to run the node
		"--datadir=" + CONSENSUS_DATA_DIRPATH_ON_SERVICE_CONTAINER,
		"--chain-config-file=" + genesis_config_filepath,
		"--genesis-state=" + genesis_ssz_filepath,
		"--http-web3provider=" + el_client_engine_rpc_url_str,
		"--rpc-host=" + PRIVATE_IP_ADDRESS_PLACEHOLDER,
		"--rpc-port={0}".format(RPC_PORT_NUM),
		"--grpc-gateway-host=0.0.0.0",
		"--grpc-gateway-port={0}".format(HTTP_PORT_NUM),
		"--p2p-tcp-port={0}".format(DISCOVERY_TCP_PORT_NUM),
		"--p2p-udp-port={0}".format(DISCOVERY_UDP_PORT_NUM),
		"--min-sync-peers={0}".format(MIN_PEERS),
		"--monitoring-host=" + PRIVATE_IP_ADDRESS_PLACEHOLDER,
		"--monitoring-port={0}".format(BEACON_MONITORING_PORT_NUM),
		"--verbosity=" + log_level,
		# Set per Pari's recommendation to reduce noise
		"--subscribe-all-subnets=true",
		"--jwt-secret={0}".format(jwt_secret_filepath),
		# vvvvvvvvv METRICS CONFIG vvvvvvvvvvvvvvvvvvvvv
		"--disable-monitoring=false",
		"--monitoring-host=" + PRIVATE_IP_ADDRESS_PLACEHOLDER,
		"--monitoring-port={0}".format(BEACON_MONITORING_PORT_NUM)
		# ^^^^^^^^^^^^^^^^^^^ METRICS CONFIG ^^^^^^^^^^^^^^^^^^^^^
	]

	if bootnode_context != None:
		cmd_args.append("--bootstrap-node="+bootnode_context.enr)

	if mev_boost_context != None:
		cmd_args.append(("--http-mev-relay{0}".format(mev_boost_endpoint(mev_boost_context))))

	if len(extra_params) > 0:
		# we do the for loop as otherwise its a proto repeated array
		cmd_args.extend([param for param in extra_params])

	return struct(
		container_image_name = beacon_image,
		used_ports = BEACON_NODE_USED_PORTS,
		cmd_args = cmd_args,
		files_artifact_mount_dirpaths = {
			genesis_data.files_artifact_uuid: GENESIS_DATA_MOUNT_DIRPATH_ON_SERVICE_CONTAINER,
		},
		privaite_ip_address_placeholder = PRIVATE_IP_ADDRESS_PLACEHOLDER
	)


def get_validator_service_config(
		genesis_data,
		validator_image,
		service_id,
		log_level,
		beacon_rpc_endpoint,
		beacon_http_endpoint,
		node_keystore_files,
		mev_boost_context,
		extra_params,
		prysm_password_relative_filepath,
		prysm_password_artifact_uuid
	):

	consensus_data_dirpath = path_join(CONSENSUS_DATA_DIRPATH_ON_SERVICE_CONTAINER, service_id)
	prysm_keystore_dirpath = path_join(VALIDATOR_KEYS_MOUNT_DIRPATH_ON_SERVICE_CONTAINER, node_keystore_files.prysm_relative_dirpath)
	prysm_password_filepath = path_join(PRYSM_PASSWORD_MOUNT_DIRPATH_ON_SERVICE_CONTAINER, prysm_password_relative_filepath)

	cmd_args = [
		"--accept-terms-of-use=true",#it's mandatory in order to run the node
		"--prater",                  #it's a tesnet setup, it's mandatory to set a network (https://docs.prylabs.network/docs/install/install-with-script#before-you-begin-pick-your-network-1)
		"--beacon-rpc-gateway-provider=" + beacon_http_endpoint,
		"--beacon-rpc-provider=" + beacon_rpc_endpoint,
		"--wallet-dir=" + prysm_keystore_dirpath,
		"--wallet-password-file=" + prysm_password_filepath,
		"--datadir=" + consensus_data_dirpath,
		"--monitoring-port={0}".format(VALIDATOR_MONITORING_PORT_NUM),
		"--verbosity=" + log_level,
		# TODO SOMETHING ABOUT JWT
		# vvvvvvvvvvvvvvvvvvv METRICS CONFIG vvvvvvvvvvvvvvvvvvvvv
		"--disable-monitoring=false",
		"--monitoring-host=0.0.0.0",
		"--monitoring-port={0}".format(VALIDATOR_MONITORING_PORT_NUM)
		# ^^^^^^^^^^^^^^^^^^^ METRICS CONFIG ^^^^^^^^^^^^^^^^^^^^^
	]

	if mev_boost_context != None:
		# TODO required to work?
		# cmdArgs = append(cmdArgs, "--suggested-fee-recipient=0x...")
		cmd_args.append("--enable-builder")


	if len(extra_params) > 0:
		# we do the for loop as otherwise its a proto repeated array
		cmd_args.extend([param for param in extra_params])


	return struct(
		container_image_name = validator_image,
		used_ports = VALIDATOR_NODE_USED_PORTS,
		cmd_args = cmd_args,
		files_artifact_mount_dirpaths = {
			genesis_data.files_artifact_uuid: GENESIS_DATA_MOUNT_DIRPATH_ON_SERVICE_CONTAINER,
			node_keystore_files.files_artifact_uuid:             VALIDATOR_KEYS_MOUNT_DIRPATH_ON_SERVICE_CONTAINER,
			prysm_password_artifact_uuid:          PRYSM_PASSWORD_MOUNT_DIRPATH_ON_SERVICE_CONTAINER,			
		},
		privaite_ip_address_placeholder = PRIVATE_IP_ADDRESS_PLACEHOLDER
	)


def new_prysm_launcher(genesis_data, prysm_password_relative_filepath, prysm_password_artifact_uuid):
	return struct(
		genesis_data = genesis_data,
		prysm_password_artifact_uuid = prysm_password_artifact_uuid,
		prysm_password_relative_filepath = prysm_password_relative_filepath
	)
