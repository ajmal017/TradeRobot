from ib_insync import *

# util.startLoop() # uncomment this line when in a jupyter notebook
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)
if ib.isConnected():
    print('TWS connection successful.')
ib.disconnect()
