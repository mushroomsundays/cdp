import pandas as pd
from datetime import datetime
from pycoingecko import CoinGeckoAPI
from simplegmail import Gmail
import gspread
from maps import currency_map


def get_current_prices(currencies: list, vs_currencies: list) -> dict:
    """
    Get current crypto prices from CoinGecko API
    currencies example: ['bitcoin', 'ethereum', 'avalanche-2', 'terra-luna']
    vs_currencies example: ['usd']
    """
    # create client
    cg = CoinGeckoAPI()

    # ping CoinGecko server
    if cg.ping():
        
        # TODO: add try/except block
        # what type of exception happens when cg.get_price fails?
        prices_dict = cg.get_price(ids=currencies, vs_currencies=vs_currencies)
        
        return prices_dict

    return {}
    
def read_sheet(doc_name: str, sheet: str, _range='all') -> pd.DataFrame:
    """
    Read a spreadsheet (or a range of cells) into a Pandas DataFrame
    """
    # service account credentials for gspread are stored here: 
    # '~/.config/gspread/service_account.json'
    gc = gspread.service_account()

    doc = gc.open(doc_name)
    obj = getattr(doc, sheet)

    if _range == 'all':
        list_content = obj.get_all_values()
    else:
        list_content = obj.get(_range)

    # convert to DataFrame with first row as header
    df = pd.DataFrame(list_content)
    new_header = df.iloc[0]
    df = df[1:]
    df.columns = new_header


    return df

def fill_cell(doc_name, sheet, key_cell, value):
    """
    Fills a single cell in a Google sheet
    """

    gc = gspread.service_account()
    doc = gc.open(doc_name)
    obj = getattr(doc, sheet)

    # update a single cell
    obj.update(key_cell, value)

    # Format the header
    #obj.format('A1:B1', {'textFormat': {'bold': True}})

def send_gmail(
    to: str,
    _from: str,
    subject: str,
    message: str,
    signature=True) -> None:

    gmail = Gmail() # will open a browser window to ask you to log in and authenticate

    params = {
    "to": to,
    "sender": _from,
    "subject": subject,
    #"msg_html": "<h1>Woah, my first email!</h1><br />This is an HTML email.",
    #"msg_plain": "Hi\nThis is a plain text email.",
    "msg_plain": message,
    "signature": signature  # use my account signature
    }

    # TODO: try/except block
    message = gmail.send_message(**params)  # equivalent to send_message(to="you@youremail.com", sender=...)

def check_health_factors(
    df: pd.DataFrame, 
    min_health_factor: float,
    email_to: str,
    email_from: str) -> list: 
    """
    Looks for column 'Health' in a DataFrame
    Loops through 'Health' column looking for values below min_health_factor
    On a hit, sends an email notification
    """

    if not 'Health' in df.columns:
        return 
    
    positions_healthy = True
    for i,row in df.iterrows():
        try:
            health_factor = float(row['Health'])
        except ValueError:
            continue
        if health_factor < min_health_factor:
            positions_healthy = False
            msg = f"Your collateralized debt position on \
                {row['Protocol']} ({row['Blockchain']}) is \
                unhealthy with a health factor of {row['Health']}"

            send_gmail(
                to=email_to,
                _from=email_from,
                subject="CDP HEALTH FACTOR ALERT",
                message=msg
            )
            
    if positions_healthy:
        return True

    return False
        