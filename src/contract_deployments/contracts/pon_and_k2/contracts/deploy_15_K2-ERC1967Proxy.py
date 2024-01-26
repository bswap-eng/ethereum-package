from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware
import os
import time
import logging

# Account Alias: PON
ACCOUNT_ALIAS = "PON"

# ERC1967Proxy contract bytecode
BYTE_CODE = "0x60806040526040516104e13803806104e1833981016040819052610022916102de565b61002e82826000610035565b50506103fb565b61003e83610061565b60008251118061004b5750805b1561005c5761005a83836100a1565b505b505050565b61006a816100cd565b6040516001600160a01b038216907fbc7cd75a20ee27fd9adebab32041f755214dbc6bffa90cc0225b39da2e5c2d3b90600090a250565b60606100c683836040518060600160405280602781526020016104ba60279139610180565b9392505050565b6001600160a01b0381163b61013f5760405162461bcd60e51b815260206004820152602d60248201527f455243313936373a206e657720696d706c656d656e746174696f6e206973206e60448201526c1bdd08184818dbdb9d1c9858dd609a1b60648201526084015b60405180910390fd5b7f360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc80546001600160a01b0319166001600160a01b0392909216919091179055565b6060600080856001600160a01b03168560405161019d91906103ac565b600060405180830381855af49150503d80600081146101d8576040519150601f19603f3d011682016040523d82523d6000602084013e6101dd565b606091505b5090925090506101ef868383876101f9565b9695505050505050565b60608315610268578251600003610261576001600160a01b0385163b6102615760405162461bcd60e51b815260206004820152601d60248201527f416464726573733a2063616c6c20746f206e6f6e2d636f6e74726163740000006044820152606401610136565b5081610272565b610272838361027a565b949350505050565b81511561028a5781518083602001fd5b8060405162461bcd60e51b815260040161013691906103c8565b634e487b7160e01b600052604160045260246000fd5b60005b838110156102d55781810151838201526020016102bd565b50506000910152565b600080604083850312156102f157600080fd5b82516001600160a01b038116811461030857600080fd5b60208401519092506001600160401b038082111561032557600080fd5b818501915085601f83011261033957600080fd5b81518181111561034b5761034b6102a4565b604051601f8201601f19908116603f01168101908382118183101715610373576103736102a4565b8160405282815288602084870101111561038c57600080fd5b61039d8360208301602088016102ba565b80955050505050509250929050565b600082516103be8184602087016102ba565b9190910192915050565b60208152600082518060208401526103e78160408501602087016102ba565b601f01601f19169190910160400192915050565b60b1806104096000396000f3fe608060405236601057600e6013565b005b600e5b601f601b6021565b6058565b565b600060537f360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc546001600160a01b031690565b905090565b3660008037600080366000845af43d6000803e8080156076573d6000f35b3d6000fdfea2646970667358221220c916ec17f19f491d8f4a1f5375ef8df31d4bbb1af784a6d68d19fcf4f97c1d7d64736f6c63430008140033416464726573733a206c6f772d6c6576656c2064656c65676174652063616c6c206661696c65640000000000000000000000003aa5ebb10dc797cac828524e59a333d0a371443c000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000e49065714700000000000000000000000068b1d87f95878fe05b998f19b66f4baba5de1aed000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000000000094b322d5245504f525400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001310000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"

logging.basicConfig(filename="/tmp/K2_ERC1967Proxy_deployment.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

def deploy_K2_ERC1967Proxy() -> (bool, dict):
    
    result = {
        "transaction": {},
        "receipt": {},
        "additional_info": {
            "contract_address": "" # Only populates if the contract was deployed successfully
        }
    }
    
    el_uri = os.getenv("EL_RPC_URI", 'http://0.0.0.0:53913')
    sender = get_sender()
    receiver = "0x0000000000000000000000000000000000000000"
    w3 = Web3(Web3.HTTPProvider(el_uri))
    # sleep for 10s before checking again
    time.sleep(10)
    
    # Check if the chain has started before submitting transactions
    block = w3.eth.get_block('latest')
    
    logging.info(f"Latest block number: {block.number}")
    if block.number > 1:
        logging.info("Chain has started, proceeding with PoN-ERC1967Proxy deployment")
        sender_account = w3.eth.account.from_key(sender)
        
        w3.middleware_onion.add(construct_sign_and_send_raw_middleware(sender_account))
        
        logging.info("Preparing PoN-ERC1967Proxy deployment tx")
        transaction = {
            "from": sender_account.address,
            "to": receiver,
            "value": 0,
            "gasPrice": w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(sender_account.address),
            "data": BYTE_CODE
        }
        
        logging.info("Estimating gas")
        estimated_gas = w3.eth.estimate_gas(transaction)
        transaction["gas"] = estimated_gas
        
        logging.info("Sending PoN-ERC1967Proxy deployment tx")
        logging.debug(f"Sending deployment tx: {transaction}")
        tx_hash = w3.eth.send_transaction(transaction)
        
        time.sleep(10)
        ERC1967Proxy_tx = w3.eth.get_transaction(tx_hash)
        ERC1967Proxy_receipt = w3.eth.get_transaction_receipt(tx_hash)
        
        logging.info(f"PoN-ERC1967Proxy deployment tx: {ERC1967Proxy_tx}")
        logging.info(f"PoN-ERC1967Proxy deployment receipt: {ERC1967Proxy_receipt}")
        
        if ERC1967Proxy_receipt['status'] == 1:
            logging.info("PoN-ERC1967Proxy deployment successful")
            result["transaction"] = ERC1967Proxy_tx
            result["receipt"] = ERC1967Proxy_receipt
            result["additional_info"]["contract_address"] = ERC1967Proxy_receipt["contractAddress"]
            return True, result
        else:
            logging.info("PoN-ERC1967Proxy deployment failed")
            return False, result
        
    else:
        logging.info("Chain has not started, restarting deployment")
        return False, {}

def get_sender() -> str:
    # Extract the right private key from the list of private keys
    private_keys = os.getenv("PRIVATE_KEYS", ACCOUNT_ALIAS+":ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80")
    private_keys.split(";")
    sender = ""
    for key in private_keys:
        if key.split(":")[0] == ACCOUNT_ALIAS:
            sender_keys = key.split(":")[1].split(",")
            sender = sender_keys[0]
            break
    return sender

def run_till_deployed() -> dict:
    deployment_status = False
    deployment_details = {}
    while deployment_status is False:
        try:
          deployment_status, deployment_details = deploy_K2_ERC1967Proxy()
        except Exception as e:
          logging.error(e)
          logging.error("restarting deployment as previous one failed")
    
    return deployment_details


if __name__ == "__main__":
    
    logging.info("PoN-ERC1967Proxy deployment started")
    deployment_details = run_till_deployed()
    logging.info("PoN-ERC1967Proxy deployment finished")
    
    print(deployment_details)
