import requests
import time


def get_price():
    response = requests.get("https://api.pancakeswap.info/api/v2/tokens"
                            "/0xba2ae424d960c26247dd6c32edc70b295c744c43").json()
    return float(response["data"]["price_BNB"])


with open("logs.borsch_swap", "w") as f:
    while True:
        f.write(str(get_price()) + '\n')
        time.sleep(1)

