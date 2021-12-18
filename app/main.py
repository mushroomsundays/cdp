import time, logging
import pandas as pd 
from collections import defaultdict
from utils import *
from maps import currency_map, alphabet_map
from email_addrs import email_to, email_from
from pycoingecko import CoinGeckoAPI
from simplegmail import Gmail
import gspread

# TODO: sleep & restart loop when terminated
# TODO: add try/except sleep & retry around all API calls

# NOTE: 
# 1. ConnectionResetError
# 2. urllib3.exceptions.ProtocolError
# 3. requests.exceptions.ConnectionError


logging.basicConfig(
    filename="cdp_log.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S"
)

CURRENCIES = [ k for k in currency_map.keys() ]
              
DOC_NAME = 'defi_master'
SHEET = 'sheet1'
MIN_HEALTH_FACTOR = 1.8

def get_prices(num_tries=3, delay=30):
    """
    Returns a dictionary like {'ETH': 'usd', 4039.02}
    """
    # get current crypto prices
    while num_tries > 0:
        try:
            prices_dict = get_current_prices(
                currencies=CURRENCIES,
                vs_currencies='usd'
            )
            # continue when we successfully get prices
            num_tries = 0
            logging.info(f"Prices fetched for {CURRENCIES}")

            # make dict with tickers as keys instead of CoinGecko coins
            ticker_prices_dict = defaultdict()
            for i,k in enumerate(prices_dict.keys()):
                ticker = currency_map[k]
                ticker_prices_dict[ticker] = prices_dict[k]
            
            return ticker_prices_dict

        except ConnectionResetError:
            logging.info(f"CoinGecko ping failed. Waiting 30s...")
            num_tries -= 1
            time.sleep(delay)
    return

def update_sheet(df: pd.DataFrame, ticker_prices_dict: dict) -> None:
    # loop through sheet and update prices
    try:
        tickers = [ currency_map[x] for x in CURRENCIES ]
    except KeyError:
        logging.info("One or more of your currencies are not keys in currency_map")

    for i,row in df.iterrows():
        for j,cell in enumerate(row):
            if cell in tickers: # check for cells matching valid tickers
                # store the cell coordinate e.g. D2
                ticker_coordinate = alphabet_map[j] + str(i+1)
                logging.info(f"Ticker {cell} found at {ticker_coordinate}")

                # update the adjascent cell with the new price
                price_coordinate = alphabet_map[j+1] + str(i+1)
                new_price = ticker_prices_dict[cell]['usd']

                fill_cell(
                    doc_name=DOC_NAME,
                    sheet=SHEET,
                    key_cell=price_coordinate,
                    value=new_price
                )
                logging.info(f"{price_coordinate} updated to {new_price}. Sleeping for 3s...")
                time.sleep(3)

    logging.info("Done updating sheet.")
    time.sleep(3)

def main():
    """
    Assumes prices are located in cells adjascent (to the right) of tickers
    """

    global MIN_HEALTH_FACTOR
    
    while True:
        ticker_prices_dict = get_prices()

        # read current sheet and update prices
        df = read_sheet(
            doc_name=DOC_NAME,
            sheet=SHEET,
            _range='all'
        )
        logging.info(f"{SHEET} from {DOC_NAME} read")

        # update prices
        update_sheet(df, ticker_prices_dict)

        # read sheet again before checking health factors

        # MIN_HEALTH_FACTOR decreases by 10% every time an email is sent
        logging.info("Checking health factors...")
        is_healthy = check_health_factors(
            df=df,
            min_health_factor=MIN_HEALTH_FACTOR,
            email_to=email_to,
            email_from=email_from
        )
        time.sleep(3)

        if is_healthy:
            logging.info("All positions are healthy")
        else:
            logging.info("POSITION UNHEALTHY; CHECK EMAIL")
            
            # decrease min health factor by 10% after an email
            MIN_HEALTH_FACTOR = MIN_HEALTH_FACTOR * 0.9
            logging.info(f"Minimum health factor decreased to {MIN_HEALTH_FACTOR}")
        
        time.sleep(60)

    # TODO: send email on termination; sleep for X and then retry

if __name__ == "__main__":
    main()