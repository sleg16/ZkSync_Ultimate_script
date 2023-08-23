import json
import time
from web3 import Web3
from loguru import logger


with open('config.json', 'r') as f:
    config = json.load(f)

withdraw_amount = float(config['withdraw_amount'])
delay_between_txns = int(config['delay_between_txns'])
gas = int(config['gas'])

zk_rpc_url = "https://mainnet.era.zksync.io"
web3 = Web3(Web3.HTTPProvider(zk_rpc_url))

with open('private_key.txt', 'r') as file:
    private_keys = [row.strip() for row in file]

with open('okex_wallets.txt', 'r') as file:
    okex_addresses = [web3.to_checksum_address(row.strip()) for row in file]

def build_txn(*, web3: Web3, from_address: str, to_address: str, amount: float) -> dict[str, int | str]:
    nonce = web3.eth.get_transaction_count(from_address)
    txn = {
        'chainId': 324,
        'from': from_address,
        'to': to_address,
        'value': int(Web3.to_wei(amount, 'ether')),
        'nonce': nonce,
        'gasPrice': web3.eth.gas_price,
        'gas': gas,
    }
    return txn

choice = input("Введите 1 для проверки баланса ETH или 2 для вывода или 'q' чтобы выйти: ")

if choice == "1":
    for private_key in private_keys:
        address = web3.to_checksum_address(web3.eth.account.from_key(private_key=private_key).address)
        balance = web3.eth.get_balance(address)
        eth_balance = round(Web3.from_wei(balance, 'ether'),6)
        logger.success(f"Баланс адреса {address}: {eth_balance} ETH")
elif choice == "2":
    for private_key, okex_address in zip(private_keys, okex_addresses):
        wallet_address = web3.to_checksum_address(web3.eth.account.from_key(private_key=private_key).address)
        transaction = build_txn(web3=web3, from_address=wallet_address, to_address=okex_address, amount=withdraw_amount)
        signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
        txn_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        logger.success(f"Транзакция отправлена с {wallet_address} на {okex_address} с хешем {txn_hash.hex()}")
        time.sleep(delay_between_txns)
elif choice == "q":
    logger.info("Скрипт завершён")
