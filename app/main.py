# general
import time, logging
import pandas as pd 
from datetime import datetime
from collections import defaultdict
from urllib3.exceptions import ReadTimeoutError

# local
from utils import *
from maps import currency_map, alphabet_map
from email_addrs import email_to, email_from

# API libraries
from pycoingecko import CoinGeckoAPI
from simplegmail import Gmail
import gspread

# TODO: sleep & restart loop when terminated
# TODO: add try/except sleep & retry around all API calls

# NOTE: 
# 1. ConnectionResetError
# 2. urllib3.exceptions.ProtocolError
# 3. requests.exceptions.ConnectionError

"""
Traceback (most recent call last):
  File "/home/jmoore87jr/.virtualenvs/cryptoenv/lib/python3.8/site-packages/urllib3/connection.py", line 169, in _new_conn
    conn = connection.create_connection(
  File "/home/jmoore87jr/.virtualenvs/cryptoenv/lib/python3.8/site-packages/urllib3/util/connection.py", line 73, in create_connection
    for res in socket.getaddrinfo(host, port, family, socket.SOCK_STREAM):
  File "/usr/lib/python3.8/socket.py", line 918, in getaddrinfo
    for res in _socket.getaddrinfo(host, port, family, type, proto, flags):
socket.gaierror: [Errno -3] Temporary failure in name resolution

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/jmoore87jr/.virtualenvs/cryptoenv/lib/python3.8/site-packages/urllib3/connectionpool.py", line 699, in urlopen
    httplib_response = self._make_request(
  File "/home/jmoore87jr/.virtualenvs/cryptoenv/lib/python3.8/site-packages/urllib3/connectionpool.py", line 382, in _make_request
    self._validate_conn(conn)
  File "/home/jmoore87jr/.virtualenvs/cryptoenv/lib/python3.8/site-packages/urllib3/connectionpool.py", line 1010, in _validate_conn
    conn.connect()
  File "/home/jmoore87jr/.virtualenvs/cryptoenv/lib/python3.8/site-packages/urllib3/connection.py", line 353, in connect
    conn = self._new_conn()
  File "/home/jmoore87jr/.virtualenvs/cryptoenv/lib/python3.8/site-packages/urllib3/connection.py", line 181, in _new_conn
    raise NewConnectionError(
urllib3.exceptions.NewConnectionError: <urllib3.connection.HTTPSConnection object at 0x7f93d7596760>: Failed to establish a new connection: [Errno -3] Temporary failure in name resolution

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/jmoore87jr/.virtualenvs/cryptoenv/lib/python3.8/site-packages/requests/adapters.py", line 439, in send
    resp = conn.urlopen(
  File "/home/jmoore87jr/.virtualenvs/cryptoenv/lib/python3.8/site-packages/urllib3/connectionpool.py", line 755, in urlopen
    retries = retries.increment(
  File "/home/jmoore87jr/.virtualenvs/cryptoenv/lib/python3.8/site-packages/urllib3/util/retry.py", line 573, in increment
    raise MaxRetryError(_pool, url, error or ResponseError(cause))
urllib3.exceptions.MaxRetryError: HTTPSConnectionPool(host='sheets.googleapis.com', port=443): Max retries exceeded with url: /v4/spreadsheets/1vnADeRKAhCnK5HSRyoz5ValE_zjZyKCcANSsg-0w0uk?includeGridData=false (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x7f93d7596760>: Failed to establish a new connection: [Errno -3] Temporary failure in name resolution'))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "main.py", line 159, in <module>
    main()
  File "main.py", line 122, in main
    update_sheet(prices_df, ticker_prices_dict)
  File "main.py", line 90, in update_sheet
    fill_cell(
  File "/home/jmoore87jr/crypto/cdp2/app/utils.py", line 60, in fill_cell
    doc = gc.open(doc_name)
  File "/home/jmoore87jr/.virtualenvs/cryptoenv/lib/python3.8/site-packages/gspread/client.py", line 127, in open
    return Spreadsheet(self, properties)
  File "/home/jmoore87jr/.virtualenvs/cryptoenv/lib/python3.8/site-packages/gspread/spreadsheet.py", line 33, in __init__
    metadata = self.fetch_sheet_metadata()
  File "/home/jmoore87jr/.virtualenvs/cryptoenv/lib/python3.8/site-packages/gspread/spreadsheet.py", line 243, in fetch_sheet_metadata
    r = self.client.request("get", url, params=params)
  File "/home/jmoore87jr/.virtualenvs/cryptoenv/lib/python3.8/site-packages/gspread/client.py", line 59, in request
    response = getattr(self.session, method)(
  File "/home/jmoore87jr/.virtualenvs/cryptoenv/lib/python3.8/site-packages/requests/sessions.py", line 555, in get
    return self.request('GET', url, **kwargs)
  File "/home/jmoore87jr/.virtualenvs/cryptoenv/lib/python3.8/site-packages/google/auth/transport/requests.py", line 480, in request
    response = super(AuthorizedSession, self).request(
  File "/home/jmoore87jr/.virtualenvs/cryptoenv/lib/python3.8/site-packages/requests/sessions.py", line 542, in request
    resp = self.send(prep, **send_kwargs)
  File "/home/jmoore87jr/.virtualenvs/cryptoenv/lib/python3.8/site-packages/requests/sessions.py", line 655, in send
    r = adapter.send(request, **kwargs)
  File "/home/jmoore87jr/.virtualenvs/cryptoenv/lib/python3.8/site-packages/requests/adapters.py", line 516, in send
    raise ConnectionError(e, request=request)
requests.exceptions.ConnectionError: HTTPSConnectionPool(host='sheets.googleapis.com', port=443): Max retries exceeded with url: /v4/spreadsheets/1vnADeRKAhCnK5HSRyoz5ValE_zjZyKCcANSsg-0w0uk?includeGridData=false (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x7f93d7596760>: Failed to establish a new connection: [Errno -3] Temporary failure in name resolution'))
"""


logging.basicConfig(
    filename="cdp_log.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S"
)

CURRENCIES = [ k for k in currency_map.keys() ]           
DOC_NAME = 'defi_master'
PRICES_SHEET = 'asset_prices'
CDP_SHEET = 'CDPs'
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
                    sheet_name=PRICES_SHEET,
                    key_cell=price_coordinate,
                    value=new_price
                )

                # update 'Last Updated' column with timestamp
                timestamp_coordinate = alphabet_map[j+2] + str(i+1)
                _timestamp = datetime.now().strftime("%H:%M:%S (%Y-%m-%d)")
                fill_cell(
                    doc_name=DOC_NAME,
                    sheet_name=PRICES_SHEET,
                    key_cell=timestamp_coordinate,
                    value=_timestamp
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
        try:
            prices_df = read_sheet(
                doc_name=DOC_NAME,
                sheet_name=PRICES_SHEET,
                _range='all'
            )
            logging.info(f"{PRICES_SHEET} from {DOC_NAME} read")
        except ReadTimeoutError:
            logging.info("API error; trying again in 120 seconds")
            time.sleep(120)
            continue

        # update prices
        try:
            update_sheet(prices_df, ticker_prices_dict)
        except ReadTimeoutError:
            logging.info("API error; trying again in 120 seconds")
            time.sleep(120)
            continue

        # read sheet with position health
        try:
            cdp_df = read_sheet(
                doc_name=DOC_NAME,
                sheet_name=CDP_SHEET,
                _range='all'
            )
        except ReadTimeoutError:
            logging.info("API error; trying again in 120 seconds")
            time.sleep(120)
            continue

        # MIN_HEALTH_FACTOR decreases by 10% every time an email is sent
        logging.info("Checking health factors...")
        is_healthy = check_health_factors(
            df=cdp_df,
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