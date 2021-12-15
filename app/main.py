import time, logging
import pandas as pd 
from utils import *

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S"
)

def main():
    # NOTE: assumes prices are to the right of cells with currency tickers
    # while True...
    # search sheet for currency tickers
    # (think of a better way than looping through all cells)
    # store in a dict {cell: new_value}
    # loop through dict and call fill_cell()
    pass 

if __name__ == "__main__":
    main()