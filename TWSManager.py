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
    def __init__(self):
        self.ib = IB()

    def check_terminal_connection(self, attempt_num = 5):
        print('Checking connection with the TWS terminal...', end='')
        if not self.ib.isConnected():
            print('connection is absent.')
            return False
        print('is connected.')
        return True

    def connect_to_terminal(self, attempt_num=5):
        if self.check_terminal_connection():
            return True

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
            print(f'An error occurred after connection attempt: ', ex)
            print('Try again')
            self.check_terminal_connection(attempt_num - 1)

if not ib.isConnected():  # connect only without active connection
    try:
        print('Connecting...')
        ib.connect('127.0.0.1', 7497, clientId=1)  # connect
    except Exception as ex:
        print('Error:', ex)  # catch at exception

if ib.isConnected():
    print("Successfully connected")
