def new_mev_plus_context(private_ip_address, port):
    return struct(
        private_ip_address=private_ip_address,
        port=port,
    )


def mev_plus_endpoint(mev_plus_context):
# MEV Plus BuilderAPI endpoint
    return "http://{0}:{1}".format(
        mev_plus_context.private_ip_address, mev_plus_context.port
    )
