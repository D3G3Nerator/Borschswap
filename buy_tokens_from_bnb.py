from web3 import Web3

import time
import config
import json

bsc = "https://bsc-dataseed.binance.org/"
web3 = Web3(Web3.HTTPProvider(bsc))

print(web3.isConnected())

# адрес роутера pancakeswap
panRouterContractAddress = '0x10ED43C718714eb63d5aA57B78B54704E256024E'
dydxrouteraddress = "0x09403FD14510F8196F7879eF514827CD76960B5d"
sushi_router = "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"
one_inch_router_address = "0x1111111254fb6c44bAC0beD2854e76F90643097d"

# pancakeswap abi_1inch
panabi = json.loads(open('abi_1inch').read())
dydxabi = json.loads(open('abi_1inch').read())
sushiabi = json.loads(open("abi's/sushiswap_abi.json").read())
one_inch_abi = json.loads(open("abi's/1inch_abi.json").read())

# адрес моего кошелька
sender_address = '0x0388181A63ce0Aad90937fb318cA8Af1932Eb7CC'

balance = web3.eth.get_balance(sender_address)
humanReadable = web3.fromWei(balance, 'ether')
spend = web3.toChecksumAddress("0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c")  # wbnb contract
tokenToBuy = web3.toChecksumAddress("0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82") # busd
contract = web3.eth.contract(address=panRouterContractAddress, abi=panabi)

nonce = web3.eth.get_transaction_count(sender_address)

start = time.time()

pancakeswap2_txn = contract.functions.swapExactETHForTokens(
    0,
    [spend, tokenToBuy],
    sender_address,
    (int(time.time()) + 10000)
).buildTransaction({
    'from': sender_address,
    'value': web3.toWei(0.0003, 'ether'),  # This is the Token(BNB) amount you want to Swap from
    'gas': 180000,
    'gasPrice': web3.toWei('5', 'gwei'),
    'nonce': nonce,
})

signed_txn = web3.eth.account.sign_transaction(pancakeswap2_txn, private_key=config.private_key)
tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
print(web3.toHex(tx_token))