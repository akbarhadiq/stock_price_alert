import datetime
# for json viewer check : jsonviewer.stack.hu --> this is good
from dotenv import load_dotenv
import os
import requests
import datetime as dt

load_dotenv()

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"
STOCK_API_KEY = os.getenv("stock_api_key")
NEWS_API_KEY = os.getenv("news_api_key")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_API")
TELEGRAM_BOT_CHAT_ID = os.getenv("telegram_bot_id")

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

stock_tsla_api_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": "TSLA",
    "interval": "5min",
    "apikey": STOCK_API_KEY
}

news_api_tsla_params = {
    "qinTitle": "Tesla",
    "from": (dt.datetime.now().date() - datetime.timedelta(days=1)),
    "sortBy": "popularity",
    "apiKey": NEWS_API_KEY,
    "sources": ["bloomberg", "cnbc", "cnn"]
}

TSLA_response = requests.get(url=STOCK_ENDPOINT, params=stock_tsla_api_params)
TSLA_data = TSLA_response.json()
# print(TSLA_data)

# get yesterday closing!
# get today's date
today = dt.datetime.now()
# get yesterday's date
yesterday_date = today.date() - datetime.timedelta(days=1)

TSLA_yesterday_closing = float(TSLA_data['Time Series (Daily)'][str(yesterday_date)]['4. close'])
print(TSLA_yesterday_closing)
# convert yesterday date to str, else it passes tuples instead of str, causing an error

# --> get the day before yesterday closing price
# get the day before yesterday date data
day_before_yesterday_date = today.date() - datetime.timedelta(days=2)
TSLA_before_yesterday_closing = float(TSLA_data['Time Series (Daily)'][str(day_before_yesterday_date)]['4. close'])
print(TSLA_before_yesterday_closing)

# Find the positive difference between 1 and 2. e.g. 40 - 20 = -20, but the positive difference is 20.
price_difference = float(TSLA_yesterday_closing) - float(TSLA_before_yesterday_closing)
print(price_difference)

# find the price difference but in percentage :
percentage_difference = round((price_difference / ((TSLA_yesterday_closing + TSLA_before_yesterday_closing) / 2)) * 100,
                              2)

print(f"{percentage_difference}%")


def get_news():
    news_response = requests.get(NEWS_ENDPOINT, params=news_api_tsla_params)
    return news_response.json()


def telegram_bot_send(send_message):
    bot_token = TELEGRAM_BOT_TOKEN
    bot_chat_id = TELEGRAM_BOT_CHAT_ID
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chat_id + \
                '&parse_mode=Markdown&text=' + send_message

    response = requests.get(send_text)
    return response.json()


def report(my_message):
    telegram_bot_send(my_message)


news_list = None

if percentage_difference > 5:
    news_data = get_news()
    relevant_news_data = news_data["articles"][:3]
    news_list = []

    for articles in relevant_news_data:
        news = {
            "Headline": articles['title'],
            "Brief": articles['description'],
            "Link": articles['url']
        }

        news_list.append(news)

        for x in range(len(news_list)):
            message = f"TSLA UP/DOWN {percentage_difference}" \
                      f"{news_list[x]['Headline']} \n" \
                      f"{news_list[x]['Brief']} \n" \
                      f"{news_list[x]['Link']}"

            report(message)


else:
    message = f"No significant difference in TSLA stock price today\n" \
              f"Yesterday Closing Price : ${TSLA_yesterday_closing}\n" \
              f"Before Yesterday Closing Price: ${TSLA_before_yesterday_closing}\n" \
              f"Difference of {percentage_difference} percent"

    report(message)
