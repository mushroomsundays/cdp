# Cryptocurrency Price Updater Bot

Running `main.py` will start a bot that updates a Google Sheets spreadsheet \
with cryptocurrency prices of your choice every 30 seconds. Optionally, the bot \
can send email notifications when asset prices hit predetermined levels. \

The intended use for this bot is near-real-time tracking of collateralized debt \
positions (CDPs) to avoid liquidation.

## Setup
1. You will need to enable developer access for Sheets and Gmail. \ 
See these links: \

[Enable API Access (gspread)](https://docs.gspread.org/en/latest/oauth2.html#enable-api-access-for-a-project)

[Allow access to Gmail account (simplegmail)](https://githubhelp.com/jeremyephron/simplegmail)

You should store `client_secret.json` and `gmail_token.json` in the same folder as `main.py`.

2. Install Python packages to interract with the API's:
`pip install pycoingecko`
`pip install gspread`
`pip install simplegmail`

3. Edit `currency_map` in `maps.py` to include the currencies you want to track. \
CoinGecko Token symbols can be found [here](https://docs.google.com/spreadsheets/d/1wTTuxXt8n9q7C4NDXqQpI3wpKu1_5bGVmP9Xz0XGSyU/edit#gid=0)

4. Create a file `email_addrs.py` with `email_to = "myEmailAddress"` and `email_from = "myGmailAddress"`

5. Edit `DOC_NAME`, `PRICES_SHEET`, `CDP_SHEET`, `MIN_HEALTH_FACTOR` \
in lines 29-32 of `main.py`

6. Your asset_prices sheet should look like this: \
![example](https://imgur.com/ZfSWfYu.jpg)

7. Your CDP sheet should have a column 'Health' that calculates the health factor of your \
positions. Health factor = (max LTV / current LTV). A health factor of 1.00 means you will be liquidated.

---

## Operation

If everything is set up correctly, main.py should update your sheet every 30 seconds until \
you terminate it.








