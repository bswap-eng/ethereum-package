shared_utils = import_module("../shared_utils/shared_utils.star")
mev_plus_context_module = import_module("../mev_plus/mev_plus_context.star")
input_parser = import_module("../package_io/input_parser.star")

MEV_PLUS_PROTOCOL = "TCP"

USED_PORTS = {
    "api": shared_utils.new_port_spec(
        input_parser.PLUS_PORT, MEV_PLUS_PROTOCOL, wait="5s"
    )
}


def launch(plan, mev_plus_launcher, service_name, network_id, mev_plus_image):
    config = get_config(mev_plus_launcher, network_id, mev_plus_image)

    mev_plus_service = plan.add_service(service_name, config)

    return mev_plus_context_module.new_mev_plus_context(
        mev_plus_service.ip_address, input_parser.PLUS_PORT
    )


def get_config(mev_plus_launcher, network_id, mev_plus_image):
    command = ["mev-plus"]

    if mev_plus_launcher.should_check_relay:
        command.append("-relay-check")

    return ServiceConfig(
        image=mev_plus_image,
        ports=USED_PORTS,
        cmd=command,
        env_vars={
            "GENESIS_FORK_VERSION": "0x10000038",
            "LISTEN_ADDR": "0.0.0.0:{0}".format(
                input_parser.PLUS_PORT
            ),
            "SKIP_RELAY_SIGNATURE_CHECK": "1",
            "RELAYS": mev_plus_launcher.relay_end_points[0],
        },
    )


def new_mev_plus_launcher(should_check_relay, relay_end_points):
# TODO: Ensure the basic configuration for the entire kurtosis network is set by default
    return struct(
        should_check_relay=should_check_relay, relay_end_points=relay_end_points
    )
