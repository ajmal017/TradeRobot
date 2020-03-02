import requests
import pandas as pd
import time
import talib
import pytz
import datetime
import os
import ibapi
from ib_insync import *

# ib.connect('127.0.0.1', 7497, clientId=1)
#
# Uncomment next line when in a jupyter notebook
# util.startLoop()


class TWSManager:

    def __init__(self, api_key, interval='1day', time_series='TIME_SERIES_DAILY'):
        self.ib = IB()
        self.INTERVAL = interval
        self.API_KEY = api_key
        self.TIME_SERIES = time_series

    def check_terminal_connection(self):
        """
        The function for terminal connection check.
        It will return True if connection is exist and False in otherwise case.

        :return:
        """
        print('Checking connection with the TWS terminal...', end='')
        if not self.ib.isConnected():
            print('connection is absent.')
            return False
        print('is connected.')
        return True

    def connect_to_terminal(self, attempt_num=5):
        """
        The function will try to connect to the TWS terminal the 'attempt_num' times
        with 60 seconds delay between each attempt.

        :param attempt_num:
        :return:
        """
        n = 60   # Delay between attempts in seconds.

        if attempt_num < 1:
            print('Max connection attempts is reached.')
            return False

        try:
            print('Try to connect to TWS terminal...', end='')
            self.ib.connect('127.0.0.1', 7497, clientId=1)
            if self.ib.isConnected():
                print('connection established successful.')
                return True
        except Exception as ex:
            # Catch an exceptions
            print('an error occurred after connection attempt:', ex)
            print(f'Try again in {n} sec.')
            for i in range(n, 0, -1):
                time.sleep(1)
                # print(f'Try again in {i} sec.', end='\r')
            self.connect_to_terminal(attempt_num - 1)

    def balance(self):
        """
        Return an actual account balance.

        :return:
        """
        balances = {av.tag: float(av.value) for av in self.ib.accountSummary()
                    if av.tag in ['AvailableFunds', 'BuyingPower', 'TotalCashValue', 'NetLiquidation']}
        balance = balances.get('AvailableFunds', 0)

        return balance

    # def check_balance(self, ticker1, count):
    #     price = read_data(ticker1)['close'].iloc[-1]
    #     amount = price * count
    #     if balance() > amount:
    #         return True
    #     else:
    #         return False

    def time_check(self, ticker):
        """
        The function will return the working hours status on the stock market for the specified ticker.
        Return values: premarket, regular, postmarket or close

        :param ticker:
        :return:
        """

        contract = Stock(ticker)
        cds = self.ib.reqContractDetails(contract)
        hours = cds[0].tradingHours
        hourslist1 = hours.split(';')
        hourslist2 = hourslist1[0].split('-')
        hourslistopening = hourslist2[0].split(':')
        tz = self.get_tz(ticker)
        today = datetime.datetime.now(tz=pytz.UTC).astimezone(pytz.timezone(tz))
        date = today.strftime("%Y%m%d")
        time = today.strftime("%H%M")
        print('DateTime: ', today.strftime("%d-%m-%Y at %I:%M%p"), tz)

        if hourslistopening[1] == 'CLOSED':
            return 'close'
        else:
            hourslistclosing = hourslist2[1].split(':')
            openingsdict = dict(zip(hourslistopening[::2], hourslistopening[1::2]))
            closingdict = dict(zip(hourslistclosing[::2], hourslistclosing[1::2]))
            hoursregular = cds[0].liquidHours
            hourslist1regular = hoursregular.split(';')
            hourslist2regular = hourslist1regular[0].split('-')
            hourslistopeningregular = hourslist2regular[0].split(':')
            hourslistclosingregular = hourslist2regular[1].split(':')
            openingsdictregular = dict(zip(hourslistopeningregular[::2], hourslistopeningregular[1::2]))
            closingdictregular = dict(zip(hourslistclosingregular[::2], hourslistclosingregular[1::2]))

            rangelist = []

            for key, value in openingsdict.items():
                rangelist.append(value)

            for key, value in closingdict.items():
                rangelist.append(value)

            for key, value in openingsdictregular.items():
                rangelist.append(value)

            for key, value in closingdictregular.items():
                rangelist.append(value)

            sortrangelist = sorted(rangelist)

            if sortrangelist[0] <= time < sortrangelist[1]:
                return 'premarket'
            elif sortrangelist[1] <= time < sortrangelist[2]:
                return 'regular'
            elif sortrangelist[2] <= time < sortrangelist[3]:
                return 'postmarket'
            else:
                return 'close'

    def get_tz(self, ticker):
        """
        Get a timezone for the ticker.
        The function use a https://www.alphavantage.co/ service for check it.

        :param ticker:
        :return:
        """

        url = f'https://www.alphavantage.co/query?function={self.TIME_SERIES}&symbol={ticker}&interval=1min&apikey={self.API_KEY}'
        r = requests.get(url)
        json_data = r.json()
        tz = json_data['Meta Data']['6. Time Zone']

        return tz

    def load_data(self, ticker):
        """
        Read ticker's data to file '\Data\{ticker}.csv'

        :param ticker:
        :return:
        """
        filename = f'Data\{ticker}.csv'
        url = f'https://www.alphavantage.co/query?function={self.TIME_SERIES}&symbol={ticker}&interval={self.INTERVAL}&apikey={self.API_KEY}&datatype=csv&outputsize=compact'
        r = requests.get(url)
        content = r.content.decode('UTF-8')
        with open(filename, "w") as file:
            file.write(content)
        print(f'\tUpdate {ticker} price history:', filename)

    def read_data(self, ticker):
        """
        Read ticker's data from '\Data\{ticker}.csv'

        :param ticker:
        :return: Pandas DataFrame with stock data of ticker
        """
        df = pd.read_csv(f'\Data\{ticker}.csv')
        # os.remove(f'\Data\{ticker}.csv')
        return df
