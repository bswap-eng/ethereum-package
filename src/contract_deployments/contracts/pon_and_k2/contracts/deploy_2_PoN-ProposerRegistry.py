from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware
import os
import time
import logging

# Account Alias: PON
ACCOUNT_ALIAS = "PON"

# ProposerRegistry contract bytecode
BYTE_CODE = "0x608060405234801561001057600080fd5b506040516106cc3803806106cc83398101604081905261002f916102e0565b61003833610051565b610041826100a1565b61004a816101e0565b5050610313565b600080546001600160a01b038381166001600160a01b0319831681178455604051919092169283917f8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e09190a35050565b6001600160a01b0381166100fc5760405162461bcd60e51b815260206004820152601660248201527f496e76616c696420696d706c656d656e746174696f6e0000000000000000000060448201526064015b60405180910390fd5b610118816001600160a01b031661025960201b6101691760201c565b6101965760405162461bcd60e51b815260206004820152604360248201527f5f736574496d706c656d656e746174696f6e3a20496d706c656d656e7461746960448201527f6f6e206164647265737320646f6573206e6f742068617665206120636f6e74726064820152621858dd60ea1b608482015260a4016100f3565b600180546001600160a01b0319166001600160a01b0383169081179091556040517fbc7cd75a20ee27fd9adebab32041f755214dbc6bffa90cc0225b39da2e5c2d3b90600090a250565b6101e8610268565b6001600160a01b03811661024d5760405162461bcd60e51b815260206004820152602660248201527f4f776e61626c653a206e6577206f776e657220697320746865207a65726f206160448201526564647265737360d01b60648201526084016100f3565b61025681610051565b50565b6001600160a01b03163b151590565b6000546001600160a01b031633146102c25760405162461bcd60e51b815260206004820181905260248201527f4f776e61626c653a2063616c6c6572206973206e6f7420746865206f776e657260448201526064016100f3565b565b80516001600160a01b03811681146102db57600080fd5b919050565b600080604083850312156102f357600080fd5b6102fc836102c4565b915061030a602084016102c4565b90509250929050565b6103aa806103226000396000f3fe608060405234801561001057600080fd5b50600436106100575760003560e01c8063025b22bc1461005c5780635c60da1b14610071578063715018a61461009a5780638da5cb5b146100a2578063f2fde38b146100b3575b600080fd5b61006f61006a366004610344565b6100c6565b005b6001546001600160a01b03165b6040516001600160a01b03909116815260200160405180910390f35b61006f6100da565b6000546001600160a01b031661007e565b61006f6100c1366004610344565b6100ee565b6100ce610178565b6100d7816101d2565b50565b6100e2610178565b6100ec60006102f4565b565b6100f6610178565b6001600160a01b0381166101605760405162461bcd60e51b815260206004820152602660248201527f4f776e61626c653a206e6577206f776e657220697320746865207a65726f206160448201526564647265737360d01b60648201526084015b60405180910390fd5b6100d7816102f4565b6001600160a01b03163b151590565b6000546001600160a01b031633146100ec5760405162461bcd60e51b815260206004820181905260248201527f4f776e61626c653a2063616c6c6572206973206e6f7420746865206f776e65726044820152606401610157565b6001600160a01b0381166102215760405162461bcd60e51b815260206004820152601660248201527524b73b30b634b21034b6b83632b6b2b73a30ba34b7b760511b6044820152606401610157565b6001600160a01b0381163b6102aa5760405162461bcd60e51b815260206004820152604360248201527f5f736574496d706c656d656e746174696f6e3a20496d706c656d656e7461746960448201527f6f6e206164647265737320646f6573206e6f742068617665206120636f6e74726064820152621858dd60ea1b608482015260a401610157565b600180546001600160a01b0319166001600160a01b0383169081179091556040517fbc7cd75a20ee27fd9adebab32041f755214dbc6bffa90cc0225b39da2e5c2d3b90600090a250565b600080546001600160a01b038381166001600160a01b0319831681178455604051919092169283917f8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e09190a35050565b60006020828403121561035657600080fd5b81356001600160a01b038116811461036d57600080fd5b939250505056fea26469706673582212207eb573a583f7ae577cdb105909ecbb7add5ede7903ad5572046f98359788220a64736f6c63430008110033000000000000000000000000e7f1725e7734ce288f8367e1bb143e90bb3f0512000000000000000000000000f39fd6e51aad88f6f4ce6ab8827279cfffb92266"

logging.basicConfig(filename="/tmp/PON_ProposerRegistry_deployment.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

def deploy_PON_ProposerRegistry() -> (bool, dict):
    
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
        logging.info("Chain has started, proceeding with PoN-ProposerRegistry deployment")
        sender_account = w3.eth.account.from_key(sender)
        
        w3.middleware_onion.add(construct_sign_and_send_raw_middleware(sender_account))
        
        logging.info("Preparing PoN-ProposerRegistry deployment tx")
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
        
        logging.info("Sending PoN-ProposerRegistry deployment tx")
        logging.debug(f"Sending deployment tx: {transaction}")
        tx_hash = w3.eth.send_transaction(transaction)
        
        time.sleep(10)
        ProposerRegistry_tx = w3.eth.get_transaction(tx_hash)
        ProposerRegistry_receipt = w3.eth.get_transaction_receipt(tx_hash)
        
        logging.info(f"PoN-ProposerRegistry deployment tx: {ProposerRegistry_tx}")
        logging.info(f"PoN-ProposerRegistry deployment receipt: {ProposerRegistry_receipt}")
        
        if ProposerRegistry_receipt['status'] == 1:
            logging.info("PoN-ProposerRegistry deployment successful")
            result["transaction"] = ProposerRegistry_tx
            result["receipt"] = ProposerRegistry_receipt
            result["additional_info"]["contract_address"] = ProposerRegistry_receipt["contractAddress"]
            return True, result
        else:
            logging.info("PoN-ProposerRegistry deployment failed")
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
          deployment_status, deployment_details = deploy_PON_ProposerRegistry()
        except Exception as e:
          logging.error(e)
          logging.error("restarting deployment as previous one failed")
    
    return deployment_details


if __name__ == "__main__":
    
    logging.info("PoN-ProposerRegistry deployment started")
    deployment_details = run_till_deployed()
    logging.info("PoN-ProposerRegistry deployment finished")
    
    print(deployment_details)
