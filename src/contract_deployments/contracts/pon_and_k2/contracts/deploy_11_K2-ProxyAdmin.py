from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware
import os
import time
import logging

# Account Alias: PON
ACCOUNT_ALIAS = "PON"

# ProxyAdmin contract bytecode
BYTE_CODE = "0x608060405234801561001057600080fd5b5061001a3361001f565b61006f565b600080546001600160a01b038381166001600160a01b0319831681178455604051919092169283917f8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e09190a35050565b6106938061007e6000396000f3fe60806040526004361061007b5760003560e01c80639623609d1161004e5780639623609d1461011157806399a88ec414610124578063f2fde38b14610144578063f3b7dead1461016457600080fd5b8063204e1c7a14610080578063715018a6146100bc5780637eff275e146100d35780638da5cb5b146100f3575b600080fd5b34801561008c57600080fd5b506100a061009b366004610499565b610184565b6040516001600160a01b03909116815260200160405180910390f35b3480156100c857600080fd5b506100d1610215565b005b3480156100df57600080fd5b506100d16100ee3660046104bd565b610229565b3480156100ff57600080fd5b506000546001600160a01b03166100a0565b6100d161011f36600461050c565b610291565b34801561013057600080fd5b506100d161013f3660046104bd565b610300565b34801561015057600080fd5b506100d161015f366004610499565b610336565b34801561017057600080fd5b506100a061017f366004610499565b6103b4565b6000806000836001600160a01b03166040516101aa90635c60da1b60e01b815260040190565b600060405180830381855afa9150503d80600081146101e5576040519150601f19603f3d011682016040523d82523d6000602084013e6101ea565b606091505b5091509150816101f957600080fd5b8080602001905181019061020d91906105e2565b949350505050565b61021d6103da565b6102276000610434565b565b6102316103da565b6040516308f2839760e41b81526001600160a01b038281166004830152831690638f283970906024015b600060405180830381600087803b15801561027557600080fd5b505af1158015610289573d6000803e3d6000fd5b505050505050565b6102996103da565b60405163278f794360e11b81526001600160a01b03841690634f1ef2869034906102c990869086906004016105ff565b6000604051808303818588803b1580156102e257600080fd5b505af11580156102f6573d6000803e3d6000fd5b5050505050505050565b6103086103da565b604051631b2ce7f360e11b81526001600160a01b038281166004830152831690633659cfe69060240161025b565b61033e6103da565b6001600160a01b0381166103a85760405162461bcd60e51b815260206004820152602660248201527f4f776e61626c653a206e6577206f776e657220697320746865207a65726f206160448201526564647265737360d01b60648201526084015b60405180910390fd5b6103b181610434565b50565b6000806000836001600160a01b03166040516101aa906303e1469160e61b815260040190565b6000546001600160a01b031633146102275760405162461bcd60e51b815260206004820181905260248201527f4f776e61626c653a2063616c6c6572206973206e6f7420746865206f776e6572604482015260640161039f565b600080546001600160a01b038381166001600160a01b0319831681178455604051919092169283917f8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e09190a35050565b6001600160a01b03811681146103b157600080fd5b6000602082840312156104ab57600080fd5b81356104b681610484565b9392505050565b600080604083850312156104d057600080fd5b82356104db81610484565b915060208301356104eb81610484565b809150509250929050565b634e487b7160e01b600052604160045260246000fd5b60008060006060848603121561052157600080fd5b833561052c81610484565b9250602084013561053c81610484565b9150604084013567ffffffffffffffff8082111561055957600080fd5b818601915086601f83011261056d57600080fd5b81358181111561057f5761057f6104f6565b604051601f8201601f19908116603f011681019083821181831017156105a7576105a76104f6565b816040528281528960208487010111156105c057600080fd5b8260208601602083013760006020848301015280955050505050509250925092565b6000602082840312156105f457600080fd5b81516104b681610484565b60018060a01b038316815260006020604081840152835180604085015260005b8181101561063b5785810183015185820160600152820161061f565b506000606082860101526060601f19601f83011685010192505050939250505056fea26469706673582212202f8ae5e724012be3cc64b67dc3af893734a57101ad9db078b4f15122e4bf693a64736f6c63430008140033"

logging.basicConfig(filename="/tmp/K2_ProxyAdmin_deployment.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

def deploy_K2_ProxyAdmin() -> (bool, dict):
    
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
        logging.info("Chain has started, proceeding with PoN-ProxyAdmin deployment")
        sender_account = w3.eth.account.from_key(sender)
        
        w3.middleware_onion.add(construct_sign_and_send_raw_middleware(sender_account))
        
        logging.info("Preparing PoN-ProxyAdmin deployment tx")
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
        
        logging.info("Sending PoN-ProxyAdmin deployment tx")
        logging.debug(f"Sending deployment tx: {transaction}")
        tx_hash = w3.eth.send_transaction(transaction)
        
        time.sleep(10)
        ProxyAdmin_tx = w3.eth.get_transaction(tx_hash)
        ProxyAdmin_receipt = w3.eth.get_transaction_receipt(tx_hash)
        
        logging.info(f"PoN-ProxyAdmin deployment tx: {ProxyAdmin_tx}")
        logging.info(f"PoN-ProxyAdmin deployment receipt: {ProxyAdmin_receipt}")
        
        if ProxyAdmin_receipt['status'] == 1:
            logging.info("PoN-ProxyAdmin deployment successful")
            result["transaction"] = ProxyAdmin_tx
            result["receipt"] = ProxyAdmin_receipt
            result["additional_info"]["contract_address"] = ProxyAdmin_receipt["contractAddress"]
            return True, result
        else:
            logging.info("PoN-ProxyAdmin deployment failed")
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
          deployment_status, deployment_details = deploy_K2_ProxyAdmin()
        except Exception as e:
          logging.error(e)
          logging.error("restarting deployment as previous one failed")
    
    return deployment_details


if __name__ == "__main__":
    
    logging.info("PoN-ProxyAdmin deployment started")
    deployment_details = run_till_deployed()
    logging.info("PoN-ProxyAdmin deployment finished")
    
    print(deployment_details)
