# Cryptocurrency Price Updater Bot

Running `main.py` will start a bot that updates a Google Sheets spreadsheet \
with cryptocurrency prices of your choice every 30 seconds. Optionally, the bot \
can send email notifications when asset prices hit predetermined levels. \

## Setup
First, you will need to enable developer access for Sheets and Gmail. \ 
See these links: \

[Enable API Access (gspread)](https://docs.gspread.org/en/latest/oauth2.html#enable-api-access-for-a-project)

[Allow access to Gmail account (simplegmail)](https://githubhelp.com/jeremyephron/simplegmail)

You should store `client_secret.json` and `gmail_token.json` in the same folder as `main.py`.
---

Next, install Python packages to interract with the API's:
`pip install pycoingecko`
`pip install gspread`
`pip install simplegmail`

---









