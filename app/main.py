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

CURRENCIES = ['bitcoin', 
              'ethereum', 
              'avalanche-2', 
              'terra-luna',
              'terrausd',
              'magic-internet-money']
              
DOC_NAME = 'defi_master'
SHEET = 'sheet1'
MIN_HEALTH_FACTOR = 1.8

def main():
    # NOTE: assumes prices are to the right of cells with currency tickers
    # while True...
    # search sheet for currency tickers
    # (think of a better way than looping through all cells)
    # store in a dict {cell: new_value}
    # loop through dict and call fill_cell()

    global MIN_HEALTH_FACTOR
    
    while True:
        # get current crypto prices
        # try 3 times with 30s sleep in between
        num_tries = 3
        while num_tries > 0:
            try:
                prices_dict = get_current_prices(
                    currencies=CURRENCIES,
                    vs_currencies='usd'
                )
                # continue when we successfully get prices
                num_tries = 0
                logging.info(f"Prices fetched for {CURRENCIES}")
            except ConnectionResetError:
                logging.info(f"CoinGecko ping failed. Waiting 30s...")
                num_tries -= 1
                time.sleep(30)

        # make dict with tickers as keys instead of CoinGecko coins
        ticker_prices_dict = defaultdict()
        for i,k in enumerate(prices_dict.keys()):
            ticker = currency_map[k]
            ticker_prices_dict[ticker] = prices_dict[k]

        # read spreadsheet containing tickers & prices
        df = read_sheet(
            doc_name=DOC_NAME,
            sheet=SHEET,
            _range='all'
        )
        logging.info(f"{SHEET} from {DOC_NAME} read")

        # check Health column for factors < MIN_HEALTH_FACTOR
        # TODO: health factor stayed at 1.9 after error and restart
        # TODO: can I do health factor check AFTER looping through sheet?
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

        logging.info("Sleeping for 60 seconds...")
        time.sleep(60)

    # TODO: send email on termination; sleep for X and then retry

if __name__ == "__main__":
    main()