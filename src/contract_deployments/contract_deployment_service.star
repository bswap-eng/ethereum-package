PYTHON_IMAGE = "ethpandaops/python-web3"
CONTRACT_DEPLOYMENT_SERVICE_NAME = "contract-deployment"

# The min/max CPU/memory that deployer can use
MIN_CPU = 10
MAX_CPU = 100
MIN_MEMORY = 10
MAX_MEMORY = 300

def launch_contract_deployment_service(plan, sender_accounts, el_uri, persistent):
    contract_deployer_script = plan.upload_files(
        src = "./contract_deployer.py",
        name = "contract_deployer",
    )

    account_private_keys_str = ""
    account_keys = {} # Alias to list of private keys
    for account in sender_accounts:
        keys = account_keys.get(account.alias if account.alias else "_", [])
        account_keys[account.alias if account.alias else "_"] = keys + [account.private_key]
    
    for alias, keys in account_keys.items():
        account_private_keys_str += alias + ":" + ",".join(keys) + ";"
    account_private_keys_str = account_private_keys_str[:-1]

    # Create the python enclave service that all deployments will run in to completion
    plan.add_service(
        name = CONTRACT_DEPLOYMENT_SERVICE_NAME,
        config = ServiceConfig(
            image = PYTHON_IMAGE,
            files = {"/tmp": contract_deployer_script},
            cmd = ["/bin/sh", "-c", "touch /tmp/contract_deployer.log && tail -f /tmp/contract_deployer.log"],
            env_vars = {
                "PRIVATE_KEYS": account_private_keys_str,
                "EL_RPC_URI": el_uri,
            },
            min_cpu = MIN_CPU,
            max_cpu = MAX_CPU,
            min_memory = MIN_MEMORY,
            max_memory = MAX_MEMORY,
        ),
    )

    plan.exec(
        service_name = CONTRACT_DEPLOYMENT_SERVICE_NAME,
        recipe = ExecRecipe(
            ["/bin/sh", "-c", "nohup python /tmp/contract_deployer.py > /dev/null 2>&1 &"],
        ),
    )
