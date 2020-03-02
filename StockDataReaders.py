import requests


class AlphaVantageReader():
    def __init__(self, api_key):
        self.API_KEY = api_key

    def load_data(self, ticker, time_series='TIME_SERIES_DAILY', interval='1day'):
        """
        Download the data of ticker from 'https://www.alphavantage.co/' to file '\Data\{ticker}.csv'
        :param ticker:
        :param time_series:
        :param interval:
        :return:
        """
        filename = f'Data\{ticker}.csv'
        url = f'https://www.alphavantage.co/query?function={time_series}&symbol={ticker}&interval={interval}&apikey={self.API_KEY}&datatype=csv&outputsize=compact'
        r = requests.get(url)
        content = r.content.decode('UTF-8')
        with open(filename, "w") as file:
            file.write(content)
        print(f'\tUpdate {ticker} price history:', filename)
