def new_mev_boost_context(private_ip_address, port, service_name):
    return struct(
        private_ip_address=private_ip_address,
        port=port,
        service_name=service_name,
    )


def mev_boost_endpoint(mev_boost_context):
    return "http://{0}:{1}".format(
        mev_boost_context.private_ip_address, mev_boost_context.port
    )
