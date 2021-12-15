import time, logging
import pandas as pd 
from collections import defaultdict
from utils import *
from maps import currency_map, alphabet_map
from email_addrs import email_to, email_from
from pycoingecko import CoinGeckoAPI
from simplegmail import Gmail
import gspread


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S"
)

CURRENCIES = ['bitcoin', 'ethereum', 'avalanche-2', 'terra-luna']
DOC_NAME = 'defi_master'
SHEET = 'sheet1'
MIN_HEALTH_FACTOR = 2

def main():
    # NOTE: assumes prices are to the right of cells with currency tickers
    # while True...
    # search sheet for currency tickers
    # (think of a better way than looping through all cells)
    # store in a dict {cell: new_value}
    # loop through dict and call fill_cell()
    
    while True:
        # get current crypto prices
        prices_dict = get_current_prices(
            currencies=CURRENCIES,
            vs_currencies='usd'
        )
        logging.info(f"Prices fetched for {CURRENCIES}")

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
        check_health_factors(
            df=df,
            min_health_factor=MIN_HEALTH_FACTOR,
            email_to=email_to,
            email_from=email_from
        )

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

        logging.info("Sleeping for 30 seconds...")
        time.sleep(30)

if __name__ == "__main__":
    main()