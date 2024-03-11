from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware
import os
import time
import logging

# Account Alias: PON
ACCOUNT_ALIAS = "PON"

# TransparentUpgradeableProxy contract bytecode
BYTE_CODE = "0x5834dd0300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000b306bf915c4d645ff596e518faf3f9669b97016"

logging.basicConfig(filename="/tmp/K2_TransparentUpgradeableProxy_execution.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

def execute_K2_TransparentUpgradeableProxy() -> (bool, dict):
    
    result = {
        "transaction": {},
        "receipt": {},
        "additional_info": {}
    }
    
    el_uri = os.getenv("EL_RPC_URI", 'http://0.0.0.0:53913')
    sender = get_sender()
    receiver = "0x68b1d87f95878fe05b998f19b66f4baba5de1aed"
    w3 = Web3(Web3.HTTPProvider(el_uri))
    # sleep for 10s before checking again
    time.sleep(10)
    
    # Check if the chain has started before submitting transactions
    block = w3.eth.get_block('latest')
    
    logging.info(f"Latest block number: {block.number}")
    if block.number > 1:
        logging.info("Chain has started, proceeding with PoN-TransparentUpgradeableProxy execution")
        sender_account = w3.eth.account.from_key(sender)
        
        w3.middleware_onion.add(construct_sign_and_send_raw_middleware(sender_account))
        
        logging.info("Preparing PoN-TransparentUpgradeableProxy execution tx")
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
        
        logging.info("Sending PoN-TransparentUpgradeableProxy execution tx")
        logging.debug(f"Sending execution tx: {transaction}")
        tx_hash = w3.eth.send_transaction(transaction)
        
        time.sleep(10)
        TransparentUpgradeableProxy_tx = w3.eth.get_transaction(tx_hash)
        TransparentUpgradeableProxy_receipt = w3.eth.get_transaction_receipt(tx_hash)
        
        logging.info(f"PoN-TransparentUpgradeableProxy execution tx: {TransparentUpgradeableProxy_tx}")
        logging.info(f"PoN-TransparentUpgradeableProxy execution receipt: {TransparentUpgradeableProxy_receipt}")
        
        if TransparentUpgradeableProxy_receipt['status'] == 1:
            logging.info("PoN-TransparentUpgradeableProxy execution successful")
            result["transaction"] = TransparentUpgradeableProxy_tx
            result["receipt"] = TransparentUpgradeableProxy_receipt
            return True, result
        else:
            logging.info("PoN-TransparentUpgradeableProxy execution failed")
            return False, result
        
    else:
        logging.info("Chain has not started, restarting execution")
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

def run_till_executed() -> dict:
    execution_status = False
    execution_details = {}
    while execution_status is False:
        try:
          execution_status, execution_details = execute_K2_TransparentUpgradeableProxy()
        except Exception as e:
          logging.error(e)
          logging.error("restarting execution as previous one failed")
    
    return execution_details


if __name__ == "__main__":
    
    logging.info("PoN-TransparentUpgradeableProxy execution started")
    execution_details = run_till_executed()
    logging.info("PoN-TransparentUpgradeableProxy execution finished")
    
    print(execution_details)
