#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import logging
import json
import os
from web3 import Web3

# ENABLE LOGGING - options, DEBUG,INFO, WARNING?
logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load up MCD and 1 Inch split contract ABIs
one_inch_split_abi = json.load(open('abi_1inch/one_inch_split.json', 'r'))
beta_one_inch_split_abi = json.load(open('abi_1inch/beta_one_inch_split.json', 'r'))
mcd_abi = json.load(open('abi_1inch/mcd_join.json', 'r'))

production = False  # False to prevent any public TX from being sent
slippage = 1

# if ETH --> DAI - (enter the amount in units Ether)
amount_to_exchange = Web3.toWei(1, 'ether')

# if DAI --> ETH (using base unit, so 1 here = 1 DAI/MCD)
amount_of_dai = Web3.toWei(5, 'ether')

one_inch_split_contract = Web3.toChecksumAddress(
    '0xC586BeF4a0992C495Cf22e1aeEE4E446CECDee0E')  # 1 inch split contract

beta_one_inch_split_contract = Web3.toChecksumAddress(
    '0x50FDA034C0Ce7a8f7EFDAebDA7Aa7cA21CC1267e')  # Beta one split contract

ethereum = Web3.toChecksumAddress(
    '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE')  # ETHEREUM

mcd_contract_address = Web3.toChecksumAddress(
    '0x6b175474e89094c44da98b954eedeac495271d0f')  # DAI Token contract address

# required - example: export ETH_PROVIDER_URL="https://mainnet.infura.io/v3/yourkeyhere77777"
if 'ETH_PROVIDER_URL' in os.environ:
    eth_provider_url = os.environ["ETH_PROVIDER_URL"]
else:
    logger.warning(
        'No ETH_PROVIDER_URL has been set! Please set that and run the script again.')
    quit()

# required - The Etheruem account that you will be making the trade/exchange from
if 'BASE_ACCOUNT' in os.environ:
    base_account = Web3.toChecksumAddress(os.environ["BASE_ACCOUNT"])
else:
    logger.warning(
        'No BASE_ACCOUNT has been set! Please set that and run the script again.')
    quit()

# private key for BASE_ACCOUNT
if 'PRIVATE_KEY' in os.environ:
    private_key = os.environ["PRIVATE_KEY"]
else:
    logger.warning(
        'No private key has been set. Script will not be able to send transactions!')
    private_key = False


def get_api_call_data(_from_coin, _to_coin, _amount_to_exchange):
    '''
    Get call data from 1Inch API
    '''
    try:
        call_data = requests.get(
            'https://api.1inch.exchange/v1.1/swap?fromTokenSymbol={0}&toTokenSymbol={1}&amount={2}&fromAddress={3}&slippage={4}'.format(_from_coin, _to_coin, _amount_to_exchange, base_account, slippage))
        logger.info('response from 1 inch generic call_data request - status code: {0}'.format(
            call_data.status_code))
        if call_data.status_code != 200:
            logger.info(
                "Undesirable response from 1 Inch! This is probably bad.")
            return False
        logger.info('get_api_call_data: {0}'.format(call_data.json()))

    except Exception as e:
        logger.warning(
            "There was a issue getting get contract call data from 1 inch: {0}".format(e))
        return False

    return call_data.json()


def get_api_quote_data(_from_coin, _to_coin, _amount_to_exchange):
    '''
    Get trade quote data from 1Inch API
    '''
    try:
        quote = requests.get(
            'https://api.1inch.exchange/v1.1/quote?fromTokenSymbol={0}&toTokenSymbol={1}&amount={2}'.format(_from_coin, _to_coin, _amount_to_exchange))
        logger.info('1inch quote reply status code: {0}'.format(
            quote.status_code))
        if quote.status_code != 200:
            logger.info(
                "Undesirable response from 1 Inch! This is probably bad.")
            return False
        print(quote)
        logger.info('get_api_quote_data: {0}'.format(quote.json()))

    except Exception as e:
        logger.exception(
            "There was an issue getting trade quote from 1 Inch: {0}".format(e))
        return False

    return quote.json()

def get_swap_quote_api(_from_coin, _to_coin, _amount_to_exchange):
    '''
    Used to hit 1Inch API GET /swapQuote endpoint - https://1inch.exchange/#/api
    '''
   
    swap_quote_url = ('https://api.1inch.exchange/v1.1/swapQuote?fromTokenSymbol={0}&toTokenSymbol={1}&amount={2}&fromAddress={3}&slippage={4}&disableEstimate={5}'.format(_from_coin, _to_coin, _amount_to_exchange, base_account, slippage, "true"))

    try:
        quote = requests.get(swap_quote_url)
        logger.info('1inch swapQuote reply status code: {0}'.format(
            quote.status_code))
        if quote.status_code != 200:
            logger.info(
                "Undesirable response from 1 Inch! This is probably bad.")
            return False

        logger.info('get_api_quote_data: {0}'.format(quote.json()))
    
    except Exception as e:
        logger.exception(
            "There was an issue getting trade quote from 1 Inch: {0}".format(e))
        return False

    return quote.json()

def one_inch_get_quote(_from_token_address, _to_token_address, _amount):
    '''
    Get quote data from one inch join contract using on-chain call
    '''
    # load our contract
    one_inch_join = web3.eth.contract(
        address=one_inch_split_contract, abi=one_inch_split_abi)

    # load beta contract
    beta_one_inch_join = web3.eth.contract(
        address=beta_one_inch_split_contract, abi=beta_one_inch_split_abi)

    # make call request to contract on the Ethereum blockchain
    contract_response = one_inch_join.functions.getExpectedReturn(
        _from_token_address, _to_token_address, _amount, 100, 0).call({'from': base_account})

    '''
    work in progress. I'm not sure that it's safe to get quotes onchain yet though
    https://github.com/CryptoManiacsZone/1inchProtocol
    The sequence of number of pieces source volume could be splitted (Works like granularity, 
    higly affects gas usage. Should be called offchain, but could be called onchain if user swaps not his own funds, 
    but this is still considered as not safe)
    '''
    parts = 10  # still not 100% what parts means here. I _think_ maybe it maps to total number of exchanges to use
    # static for now, might be better if it was dynamic
    gas_price = web3.toWei('100', 'gwei')

    beta_contract_response = beta_one_inch_join.functions.getExpectedReturnWithGas(
        _from_token_address, _to_token_address, _amount, parts, 0, gas_price *
        contract_response[0]
    ).call({'from': base_account})

    logger.info("contract response: {0}".format(contract_response))
    logger.info("beta contract response: {0}".format(beta_contract_response))
    return contract_response


def broadcast_transaction(_swap_quote, _contract_response):
    '''
    This function will craft a transaction based on the results of the get_swap_quote_api function and direct contract call and then broadcast the transaction to the Ethereum network 
    '''
    # load our contract
    one_inch_join = web3.eth.contract(
        address=one_inch_split_contract, abi=one_inch_split_abi)

    # get our nonce
    nonce = web3.eth.getTransactionCount(base_account)

    # get our min return - you could calc this manually (and maybe should) but for now i'm just going to get the min_return from a direct contract call 
    min_return = _contract_response[0]

    # use all available exchanges
    disable_flags = 0
   
    # craft our distribution list. I'm just creating a list based on order of exchanges returned, this might not be the correct order! if you are going to use this in prod, make sure this is correct first. https://github.com/CryptoManiacsZone/1inchProtocol
    
    distribution = []
    for exchange in _swap_quote['exchanges']:
        logger.info(exchange['name'] + '-' + str(exchange['part']))
        distribution.append(exchange['part'])

    logger.info("distribution list:", distribution)

    # maybe not necessary 
    from_token_address = Web3.toChecksumAddress(_swap_quote['fromToken']['address'])
    to_token_address = Web3.toChecksumAddress(_swap_quote['toToken']['address'])
 
    amount_to_exchange = _swap_quote['value']
    
    # craft transaction call data
    data = one_inch_join.encodeABI(fn_name="swap", args=[
        from_token_address, to_token_address, int(amount_to_exchange), min_return, distribution, disable_flags])

    # if ETH --> DAI then value is exchange _amount, if DAI-->ETH then value != amount_to_exchange
    if from_token_address == mcd_contract_address:
        value = 0
    else:
        value = amount_to_exchange

    tx = {
        'nonce': nonce,
        'to': one_inch_split_contract,
        'value': value,
        'gasPrice': web3.eth.gasPrice,
        'from': base_account,
        'data': data
    }

    # get gas estimate
    gas = web3.eth.estimateGas(tx)
    tx["gas"] = gas

    logger.info('transaction data: {0}'.format(tx))

    # sign and broadcast our trade
    if private_key and production == True:
        try:
            signed_tx = web3.eth.account.signTransaction(tx, private_key)
        except:
            logger.exception("Failed to created signed TX!")
            return False
        try:
            tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
            logger.info("TXID: {0}".format(web3.toHex(tx_hash)))
        except:
            logger.warning("Failed sending TX to 1 inch!")
            return False
    else:
        logger.info('No private key found! Transaction has not been broadcast!')
    

def connect_to_ETH_provider():
    try:
        web3 = Web3(Web3.HTTPProvider(eth_provider_url))
    except Exception as e:
        logger.warning(
            "There is an issue with your initial connection to Ethereum Provider: {0}".format(e))
        quit()
    return web3


# establish web3 connection
web3 = connect_to_ETH_provider()


# get_api_quote_data("ETH", "DAI", amount_to_exchange)
# one_inch_token_swap("ETH", "DAI", amount_to_exchange)

swap_quote = get_swap_quote_api("ETH", "DAI", amount_to_exchange)
contract_response= one_inch_get_quote(ethereum, mcd_contract_address, amount_to_exchange)
broadcast_transaction(swap_quote, contract_response)


