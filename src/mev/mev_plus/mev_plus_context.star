def new_mev_plus_context(private_ip_address, port, service_name):
    return struct(
        private_ip_address=private_ip_address,
        port=port,
        service_name=service_name,
    )


def mev_plus_endpoint(mev_plus_context):
    # Get MEV Plus BuilderAPI endpoint string from MEV Plus context
    return "http://{0}:{1}".format(
        mev_plus_context.private_ip_address, mev_plus_context.port
    )
