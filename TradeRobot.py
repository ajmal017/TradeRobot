import TWSManager
import StockDataReaders
import datetime

# Load api key for services
try:
    print('Load file with api keys...', end='')
    with open('Data\\Api_keys.txt') as f:
        api_keys = {}
        for line in f:
            key, value = line.split('=')
            api_keys[key] = str(value).strip()
    print('successful.')
except FileNotFoundError:
    print('file \'Data\\Api_keys.txt\' is not found. Api key set as default.')
    api_keys['alphavantage_api_key'] = 'XXXXXXXXXXXXXXX'

# av = StockDataReaders.AlphaVantageReader(api_keys['alphavantage_api_key'])
# av.load_data('SPY')

# Update all tickers in 'TickersList.csv'
dr = StockDataReaders.PandasDataReader()
dr.update_tickers_by_list(filename='TickersList.csv', path='Data\\')

# Connect to TWS terminal an check the balance
myTWS = TWSManager.TWSManager(alphavantage_api_key=api_keys['alphavantage_api_key'])
if myTWS.connect_to_terminal(2):
    print(f'Account balance: {myTWS.balance()}')


# Check possibility to buy contract
ticker = 'AAPL'
amount = 10
print(f'Checking the possibility to buy {amount} lots of \'{ticker}\'...', end='')
if myTWS.check_balance(ticker, amount):
    print('the buy is possible.')
else:
    print(f'money is NOT enough.')


