shared_utils = import_module("../../shared_utils/shared_utils.star")
mev_plus_context_module = import_module("../mev_plus/mev_plus_context.star")
mev_boost_context_module = import_module("../mev_boost/mev_boost_context.star")
input_parser = import_module("../../package_io/input_parser.star")

MEV_PLUS_PROTOCOL = "TCP"
MIN_CPU = 10
MAX_CPU = 500
MIN_MEMORY = 16
MAX_MEMORY = 256

def launch(plan, mev_plus_launcher, service_name, network_params, mev_plus_image, mev_plus_flags, global_node_selectors):
    config = get_config(mev_plus_launcher, network_params, mev_plus_image, mev_plus_flags, global_node_selectors)

    mev_plus_service = plan.add_service(service_name, config)

    return mev_plus_context_module.new_mev_plus_context(
        mev_plus_service.ip_address,
        input_parser.MEV_PLUS_BUILDER_API_PORT,
        service_name,
    )

def get_config(mev_plus_launcher, network_params, mev_plus_image, mev_plus_flags, node_selectors):
    used_ports = {
        "builderApi.listen-address": shared_utils.new_port_spec(
            input_parser.MEV_PLUS_BUILDER_API_PORT,
            MEV_PLUS_PROTOCOL,
            wait = "2m",
        ),
    }

    command = ["mevPlus"]

    # Set network params for default modules
    command.append("-blockAggregator.slot-duration")
    command.append(str(network_params.seconds_per_slot))

    if mev_plus_launcher.relay_end_points:
        command.append("-relay.genesis-fork-version")
        command.append("0x10000038")

    if mev_plus_launcher.should_check_relay and mev_plus_launcher.relay_end_points:
        command.append("-relay.relay-check")

    # Since in the ethereum-package testnet we use custom network configs the signature domains may not match, however we are sure the payload is securely from a connected relay
    if mev_plus_launcher.relay_end_points:
        command.append("-relay.skip-relay-signature-check")

    if mev_plus_launcher.external_validator_proxy_address:
        command.append("-externalValidatorProxy.address")
        command.append(str(mev_plus_launcher.external_validator_proxy_address))

    if mev_plus_launcher.relay_end_points:
        # If there are mev_endpoints to configure and connect to directly, set them
        endpoints = ",".join(mev_plus_launcher.relay_end_points)
        command.append("-relay.relay-entries")
        command.append(endpoints)

    for flag, value in mev_plus_flags.items():
        if flag == "externalValidatorProxy.address":
            # Ignore external validator proxy address flag, since it's determined by the network config with boost enabled
            continue
        elif flag == "builderApi.listen-address":
            # Ignore builder api listen address flag, since it's set via env var
            continue
        elif flag == "blockAggregator.slot-duration":
            continue
        else:
            command.append("-" + flag)
            command.append(str(value))

            if shared_utils.is_url(value):
                # If the value is a url, add it to the list of ports to wait for
                used_ports[flag] = shared_utils.new_port_spec(
                    shared_utils.get_port_from_url(value),
                    MEV_PLUS_PROTOCOL,
                    wait = "2m",
                )

    return ServiceConfig(
        image = mev_plus_image,
        ports = used_ports,
        entrypoint = [
            "bash",
            "-c",
            " ".join(command),
        ],
        env_vars = {
            "BUILDERAPI_LISTEN_ADDRESS": "0.0.0.0:{0}".format(
                input_parser.MEV_PLUS_BUILDER_API_PORT,
            ),
        },
        min_cpu=MIN_CPU,
        max_cpu=MAX_CPU,
        min_memory=MIN_MEMORY,
        max_memory=MAX_MEMORY,
        node_selectors=node_selectors,
    )

def new_mev_plus_launcher(should_check_relay, relay_end_points, external_validator_proxy_context):
    return struct(
        should_check_relay = should_check_relay,
        relay_end_points = relay_end_points,
        external_validator_proxy_address = (mev_boost_context_module.mev_boost_endpoint(external_validator_proxy_context) if external_validator_proxy_context else None),
    )
