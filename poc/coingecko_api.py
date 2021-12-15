import requests, time
from pycoingecko import CoinGeckoAPI

"""
The pycoingecko library is a wrapper for CoinGecko's API
https://github.com/man-c/pycoingecko
"""

def main():
    # create client
    cg = CoinGeckoAPI()

    # ping CoinGecko server
    status = cg.ping() 
    if status:
        print("Server status OK")

        prices = cg.get_price(ids=['bitcoin', 'ethereum', 'avalanche-2', 'terra-luna'], vs_currencies='usd')

        for k,v in prices.items():
            print(f"{k}: {v}")

    
if __name__ == "__main__":
    main()