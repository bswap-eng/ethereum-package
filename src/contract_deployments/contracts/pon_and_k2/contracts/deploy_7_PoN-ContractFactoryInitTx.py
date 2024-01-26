from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware
import os
import time
import logging

# Account Alias: PON
ACCOUNT_ALIAS = "PON"

# ContractFactory contract bytecode
BYTE_CODE = "0x1da04797000000000000000000000000f39fd6e51aad88f6f4ce6ab8827279cfffb9226600000000000000000000000000000000000000000000000000000000000000640000000000000000000000000000000000000000000000000000000000000005000000000000000000000000000000000000000000000000016345785d8a000000000000000000000000000000000000000000000000000000000000000000e000000000000000000000000000000000000000000000000000000000000001e0000000000000000000000000000000000000000000000000000000000000040000000000000000000000000070997970c51812dc3a010c7d01b50e0d17dc79c80000000000000000000000000000000000000000000000000000000000000003000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000c0000000000000000000000000000000000000000000000000000000000000001050726f706f7365725265676973747279000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001310000000000000000000000000000000000000000000000000000000000000000000000000000000000000090f79bf6eb2c4f870365e785982e1f101e93b9060000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000012000000000000000000000000000000000000000000000000000000000000001400000000000000000000000003c44cdddb6a900fa2b585dd299e03d12fa4293bc000000000000000000000000000000000000000000000000000000000000016000000000000000000000000000000000000000000000000000000000000001a0000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000105265706f7274657252656769737472790000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000013100000000000000000000000000000000000000000000000000000000000000"

logging.basicConfig(filename="/tmp/PON_ContractFactory_initialize.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

def initialize_PON_ContractFactory() -> (bool, dict):
    
    result = {
        "transaction": {},
        "receipt": {},
        "additional_info": {}
    }
    
    el_uri = os.getenv("EL_RPC_URI", 'http://0.0.0.0:53913')
    sender = get_sender()
    receiver = "0xB7f8BC63BbcaD18155201308C8f3540b07f84F5e"
    w3 = Web3(Web3.HTTPProvider(el_uri))
    # sleep for 10s before checking again
    time.sleep(10)
    
    # Check if the chain has started before submitting transactions
    block = w3.eth.get_block('latest')
    
    logging.info(f"Latest block number: {block.number}")
    if block.number > 1:
        logging.info("Chain has started, proceeding with PoN-ContractFactory initialization")
        
        # Check the to contract address is an address that is a contract on the chain
        if not w3.eth.get_code(receiver):
            logging.info("Receiver address is not a contract address")
            return False, result
        
        sender_account = w3.eth.account.from_key(sender)
        
        w3.middleware_onion.add(construct_sign_and_send_raw_middleware(sender_account))
        
        logging.info("Preparing PoN-ContractFactory initialization tx")
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
        
        logging.info("Sending PoN-ContractFactory initialization tx")
        logging.debug(f"Sending initialization tx: {transaction}")
        tx_hash = w3.eth.send_transaction(transaction)
        
        time.sleep(10)
        ContractFactory_init_tx = w3.eth.get_transaction(tx_hash)
        ContractFactory_init_receipt = w3.eth.get_transaction_receipt(tx_hash)
        
        logging.info(f"PoN-ContractFactory initialization tx: {ContractFactory_init_tx}")
        logging.info(f"PoN-ContractFactory initialization receipt: {ContractFactory_init_receipt}")
        
        if ContractFactory_init_receipt['status'] == 1:
            logging.info("PoN-ContractFactory initialization successful")
            result["transaction"] = ContractFactory_init_tx
            result["receipt"] = ContractFactory_init_receipt
            return True, result
        else:
            logging.info("PoN-ContractFactory initialization failed")
            return False, result
        
    else:
        logging.info("Chain has not started, restarting initialization")
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

def run_till_sent() -> dict:
    transaction_status = False
    transaction_details = {}
    while transaction_status is False:
        try:
          transaction_status, transaction_details = initialize_PON_ContractFactory()
        except Exception as e:
          logging.error(e)
          logging.error("reattempting transaction as previous one failed")
    
    return transaction_details


if __name__ == "__main__":
    
    logging.info("PoN-ContractFactory initial transaction started")
    transaction_details = run_till_sent()
    logging.info("PoN-ContractFactory initial transaction finished")
    
    print(transaction_details)
