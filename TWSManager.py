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

    def __del__(self):
        self.disconnect()

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
                print('successful.')
                return True
        except Exception as ex:
            # Catch an exceptions
            print('an error occurred after connection attempt:', ex)
            print(f'Try again in {n} sec.')
            for i in range(n, 0, -1):
                time.sleep(1)
                # print(f'Try again in {i} sec.', end='\r')
            self.connect_to_terminal(attempt_num - 1)

    def time_check(self, ticker):
        """
        The function will return the working hours status on the stock market for the specified ticker.
        Return values: premarket, regular, postmarket or close
        :param ticker:
        :return: Premarket, Regular session, Postmarket, Close or Uncertain
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

        message = ''

        if hourslistopening[1] == 'CLOSED':
            message = 'close'
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
                message = 'premarket'
            elif sortrangelist[1] <= time < sortrangelist[2]:
                message = 'regular'
            elif sortrangelist[2] <= time < sortrangelist[3]:
                message = 'postmarket'
            else:
                message = 'close'

        messages = {
          'premarket': 'Premarket',
          'postmarket': 'Postmarket',
          'close': 'Closed',
          'regular': 'Regular session',
        }
        return messages.get(message, 'Uncertain')

    def get_tz(self, ticker):
        """
        Get a timezone for the ticker.
        The function use a https://www.alphavantage.co/ service for check it.
        :param ticker:
        :return: Time Zone
        """

        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&interval=1day&apikey={self.API_KEY}'
        r = requests.get(url)
        json_data = r.json()
        try:
            tz = json_data['Meta Data']['5. Time Zone']
        except KeyError:
            print(f'Error: can\'t get a time zone for ticker \'{ticker}\'.')
            tz = None
        return tz

    def balance(self):
        """
        Return an actual account balance.
        :return:
        """
        balances = {av.tag: float(av.value) for av in self.ib.accountSummary()
                    if av.tag in ['AvailableFunds', 'BuyingPower', 'TotalCashValue', 'NetLiquidation']}
        balance = balances.get('AvailableFunds', 0)
        return balance

    def check_balance(self, ticker, count):
        """
        Check the available sum for buy specified ticker.
        :param ticker:
        :param count:
        :return:
        """
        price = self.read_data(ticker)['close'].iloc[0]
        amount = price * count
        if self.balance() > amount:
            return True
        else:
            return False

    def load_data(self, ticker):
        """
        Download the data of ticker from 'https://www.alphavantage.co/' to file '\Data\{ticker}.csv'
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
        Read the stock data of ticker from file '\Data\{ticker}.csv'
        :param ticker:
        :return: Pandas DataFrame with stock data of ticker
        """
        df = pd.read_csv(f'\Data\{ticker}.csv')
        # os.remove(f'\Data\{ticker}.csv')
        return df

    def list_positions(self):
        positions = self.ib.positions()
        positions = "\n".join([f"{p.contract.localSymbol} {p.position}x{p.avgCost}"
                               for p in positions])
        return positions

    def list_orders(self):
        trades = self.ib.openTrades()
        orders = "\n".join([f"{t.order.action} {t.contract.secType} {t.contract.symbol} {t.contract.localSymbol}"
                            f" {t.order.totalQuantity}x{t.order.lmtPrice}"
                            for t in trades])
        return orders

    def get_contract(self, ticker):
        contract = Stock(f'{ticker}', 'SMART', 'USD')
        self.ib.qualifyContracts(contract)
        return contract

    def buy(self, ticker, count):
        contract = self.get_contract(ticker)
        if f'{ticker}' not in self.list_positions():
            if f'{ticker}' not in self.list_orders():
                order = MarketOrder('BUY', f'{count}')
                self.ib.placeOrder(contract, order)

    def sell(self, ticker, count):
        contract = self.get_contract(ticker)
        if f'{ticker}' in self.list_positions():
            if f'{ticker}' not in self.list_orders():
                order = MarketOrder('SELL', f'{count}')
                self.ib.placeOrder(contract, order)

    def disconnect(self):
        if self.ib.isConnected():
            self.ib.disconnect()

            while self.ib.isConnected():  # wait while disconnecting
                time.sleep(1)  # sleep 1 sec on waiting
        print("Successful disconnected with TWS")
