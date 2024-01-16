TCP_PROTOCOL = "TCP"
UDP_PROTOCOL = "UDP"
HTTP_APPLICATION_PROTOCOL = "http"
NOT_PROVIDED_APPLICATION_PROTOCOL = ""
NOT_PROVIDED_WAIT = "not-provided-wait"


def new_template_and_data(template, template_data_json):
    return struct(template=template, data=template_data_json)


def path_join(*args):
    joined_path = "/".join(args)
    return joined_path.replace("//", "/")


def path_base(path):
    split_path = path.split("/")
    return split_path[-1]


def path_dir(path):
    split_path = path.split("/")
    if len(split_path) <= 1:
        return "."
    split_path = split_path[:-1]
    return "/".join(split_path) or "/"


def new_port_spec(
    number,
    transport_protocol,
    application_protocol=NOT_PROVIDED_APPLICATION_PROTOCOL,
    wait=NOT_PROVIDED_WAIT,
):
    if wait == NOT_PROVIDED_WAIT:
        return PortSpec(
            number=number,
            transport_protocol=transport_protocol,
            application_protocol=application_protocol,
        )

    return PortSpec(
        number=number,
        transport_protocol=transport_protocol,
        application_protocol=application_protocol,
        wait=wait,
    )

def get_port_from_url(url):
    """
    Get the port from a URL string.

    Args:
        url (string): The URL string.

    Returns:
        int: The port or None if not present or unable to determine.
    """
    # Find the position of the colon-slash-slash ("://") in the URL
    protocol_index = url.find("://")
    
    # If "://" is not found, check if localhost of address is present
    if protocol_index == -1:
        cursor = 0
    else:
        # Move the cursor to the position after "://" or keep at start
        cursor = protocol_index + 3
    
    slash_index = url.find("/", cursor)   
    # If no slash is found, the URL might not contain a path
    if slash_index == -1:
        host_port_part = url[cursor:]
    else:
        host_port_part = url[cursor:slash_index]

    # Split the host and port based on the colon (":") if present
    parts = host_port_part.split(":")
    
    # If only one part is found, it's likely the host; return None for port
    if len(parts) == 1:
        return None
    
    # If two parts are found, try to convert the second part to an integer (port)
    # First check if it is a digit, then check if it is in the valid port range
    if len(parts) == 2 and parts[1].isdigit() and 0 <= int(parts[1]) and int(parts[1]) <= 65535:
        return int(parts[1])
    
    # If more than two parts are found, return None for port
    return None

def is_url(input_string):
    """
    Check if a string is a URL in.

    Args:
    - input_string (string): The string to check.

    Returns:
    - bool: True if the string appears to be a URL, False otherwise.
    """
    # Check if the string starts with a known scheme or is a local address
    known_schemes = ["http", "https", "ftp", "file", "tcp", "udp", "ws", "wss", "ipfs", "git"]
    for scheme in known_schemes:
        if input_string.startswith("{}://".format(scheme)):
            return True

    # Check if the string resembles an IP address
    # First remove the port if present
    check_string = input_string
    if ":" in input_string:
        check_string = input_string.split(":")[0]
    parts = check_string.split(".")
    if len(parts) == 4:
        for part in parts:
            if not part.isdigit() or not (0 <= int(part) and int(part) <= 255):
                return False
        return True

    # Check if the string is "localhost"
    if input_string.lower().startswith("localhost"):
        return True

    return False

def get_protocol_from_url(url):
    """
    Get the protocol (scheme) from a URL string.

    Args:
        url (string): The URL string.

    Returns:
        string: The protocol (scheme) or None if not present.
    """
    # Find the position of the colon-slash-slash ("://") in the URL
    protocol_index = url.find("://")
    
    # If "://" is not found, return None
    if protocol_index == -1:
        return None
    
    # Extract the substring before the "://" as the protocol
    protocol = url[:protocol_index]
    
    return protocol

def read_file_from_service(plan, service_name, filename):
    output = plan.exec(
        service_name=service_name,
        recipe=ExecRecipe(
            command=["/bin/sh", "-c", "cat {} | tr -d '\n'".format(filename)]
        ),
    )
    return output["output"]


def zfill_custom(value, width):
    return ("0" * (width - len(str(value)))) + str(value)


def label_maker(client, client_type, image, connected_client, extra_labels):
    labels = {
        "ethereum-package.client": client,
        "ethereum-package.client-type": client_type,
        "ethereum-package.client-image": image.replace("/", "-").replace(":", "-"),
        "ethereum-package.connected-client": connected_client,
    }
    labels.update(extra_labels)  # Add extra_labels to the labels dictionary
    return labels
