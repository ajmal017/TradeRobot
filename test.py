import TWSManager

myTWS = TWSManager.TWSManager(api_key='P9DHEUMVT6580QQX')

# if myTWS.connect_to_terminal(2):
#     print(f'Account balance: {myTWS.balance()}')

myTWS.load_data('SPY')


