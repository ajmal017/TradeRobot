import TWSManager
# import StockDataReaders

# av = StockDataReaders.AlphaVantageReader(api_key='P9DHEUMVT6580QQX')
# av.load_data('SPY')

myTWS = TWSManager.TWSManager(api_key='P9DHEUMVT6580QQX')

if myTWS.connect_to_terminal(2):
    print(f'Account balance: {myTWS.balance()}')

