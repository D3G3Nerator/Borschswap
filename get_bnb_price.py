import requests


def get_price():
    response = requests.get("https://api.pancakeswap.info/api/v2/tokens"
                            "/0xba2ae424d960c26247dd6c32edc70b295c744c43").json()
    return float(response["data"]["price_BNB"])

print(get_price())


