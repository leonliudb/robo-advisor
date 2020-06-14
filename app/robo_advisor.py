# app/robo_advisor.py

import datetime
import csv
import os
import requests
import json 
from dotenv import load_dotenv

load_dotenv()

def to_usd(my_price):
    return "${0:,.2f}".format(my_price)
#
# INFO INPUTS
#

api_key = os.environ.get("ALPHAVANTAGE_API_KEY")
#print(api_key)

def get_response(symbol):
    request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
    if symbol.isalpha() and \
        num_characters < 6 :
        response = requests.get(request_url)
        parsed_response = json.loads(response.text)
        return parsed_response
    else:
        print("Sorry, please enter a properly-formed stock symbol like 'MSFT'. Please try again." )
        exit()
        
symbol = str(input("Please specify a stock symbol (e.g. AMZN) and press enter: "))
num_characters = sum(c.isalpha() for c in symbol)   

parsed_response = get_response(symbol)

if str("Error Message") in parsed_response:
    print("Sorry, unable to find any data for this stock symbol. Please try again with a valid stock symbol.")
    exit()

last_refreshed = parsed_response["Meta Data"]["3. Last Refreshed"]

tsd = parsed_response["Time Series (Daily)"]
dates = list(tsd.keys()) 

latest_day = dates[0] 
latest_close = tsd[latest_day]["4. close"]

high_prices = []
low_prices = []

for date in dates:
    high_price = tsd[date]["2. high"]
    low_price = tsd[date]["3. low"]
    high_prices.append(float(high_price))
    low_prices.append(float(low_price))

recent_high = max(high_prices)
recent_low = min(low_prices)

time_now = datetime.datetime.now() 

#
# INFO OUTPUTS
#
csv_file_path = os.path.join(os.path.dirname(__file__), "..", "data", "prices.csv")

csv_headers = ["timestamp", "open", "high", "low", "close", "volume"]

with open(csv_file_path, "w") as csv_file: 
    writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
    writer.writeheader() 
    for date in dates:
        daily_prices = tsd[date]
        writer.writerow({
            "timestamp": date,
            "open": daily_prices["1. open"],
            "high": daily_prices["2. high"],
            "low": daily_prices["3. low"],
            "close": daily_prices["4. close"],
            "volume": daily_prices["5. volume"]
        })


# DISPLAY RESULTS

formatted_time_now = time_now.strftime("%Y-%m-%d %H:%M:%S")
formatted_csv_file_path = csv_file_path.split("..")[1]

if float(latest_close) > float(recent_high) * 0.9:
    rec = "SELL"
elif float(latest_close) < float(recent_low) * 1.1:
    rec = "BUY"
else:
    rec = "HOLD or NO BUY"
    
if rec == "SELL":
    reason = "If you are considering selling this stock, now would be a good time as the price is high enough."
if rec == "BUY":
    reason = "If you are considering buying this stock, now would be a good time as the price is low enough."
if rec == "HOLD or NO BUY":
    reason = "Neither buying or selling would be a good decision now as we need to wait for a better time."


print("-------------------------")
print(f"SYMBOL: {symbol}")
print("-------------------------")
print("REQUESTING STOCK MARKET DATA...")
print(f"REQUEST AT: {formatted_time_now}")
print("-------------------------")
print(f"LATEST DAY: {last_refreshed}")
print(f"LATEST CLOSE: {to_usd(float(latest_close))}")
print(f"RECENT HIGH: {to_usd(float(recent_high))}")
print(f"RECENT LOW: {to_usd(float(recent_low))}")
print("-------------------------")
print("RECOMMENDATION:", rec)
print("RECOMMENDATION REASON:", reason)
print("-------------------------")
print(f"WRITING DATA TO CSV: {formatted_csv_file_path}")
print("-------------------------")
print("HAPPY INVESTING!")
print("-------------------------")


