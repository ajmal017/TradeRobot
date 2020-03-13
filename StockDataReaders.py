import datetime
import requests
import pandas as pd
import pandas_datareader.data as web


class AlphaVantageReader():
    def __init__(self, api_key):
        self.API_KEY = api_key

    def load_data(self, ticker, time_series='TIME_SERIES_DAILY', interval='1day', path='Data\\'):
        """
        Download the stock data of selected ticker from 'https://www.alphavantage.co/' to file '{path}{ticker}.csv'
        :param path:
        :param ticker:
        :param time_series:
        :param interval:
        :return:
        """
        filename = f'{path}{ticker}.csv'
        url = f'https://www.alphavantage.co/query?function={time_series}&symbol={ticker}&interval={interval}&apikey={self.API_KEY}&datatype=csv&outputsize=compact'
        r = requests.get(url)
        content = r.content.decode('UTF-8')
        with open(filename, "w") as file:
            file.write(content)
        print(f'\tUpdate {ticker} price history:', filename)


class PandasDataReader:
    def __init__(self):
        pass

    def yahoo_data_loader(self, ticker, start=datetime.datetime(2010, 1, 1), end=datetime.datetime.today(), path='Data\\'):
        """
        Download the stock data of selected ticker from Yahoo to file '{path}{ticker}.csv'
        :param ticker:
        :param start:
        :param end:
        :param path:
        :return:
        """
        print(f'Load ticker \'{ticker}\'...\t', end='')
        df = web.DataReader(ticker, "yahoo", start=start, end=end)
        df.to_csv(f'{path}{ticker}.csv')
        print(f'successful. Saved into file \'{path}{ticker}.csv\'')

    def update_tickers_by_list(self, filename='TickersList.csv', path='Data\\'):
        """
        Update tickers data by list.
        :param filename:
        :param path:
        :return:
        """
        # Load list of tickers, also sort it
        df = pd.read_csv(f'{path}{filename}', index_col=0)
        df = df.sort_values(by='Ticker')
        df.reset_index(drop=True, inplace=True)
        df.to_csv(f'{path}{filename}')

        tickers = df['Ticker']
        print('=' * 20, 'Update started', '=' * 20)

        for ticker in tickers:
            print(f'Update ticker \'{ticker}\'...\t', end='')

            try:
                # Load current data from {ticker}.csv file
                ticker_df = pd.read_csv(f'{path}{ticker}.csv')

                # Delete last record in data for renew it
                ticker_df.drop(ticker_df.index[-1], inplace=True)

                # Convert Date to DateTime format
                ticker_df['Date'] = ticker_df['Date'].astype('datetime64[ns]')

                # Set start and end date for update data
                start = ticker_df['Date'].max().date()
                end = datetime.datetime.today().date()

                # Check last date in data
                # if start > end:
                #     print(f'up to date.')
                #     continue

                # Load new data
                new_ticker_df = web.DataReader(ticker, "yahoo", start=start, end=end).reset_index()

                # Looking for a first position in new data (Data from Yahoo has some overlays in start of period.)
                idx = new_ticker_df[new_ticker_df['Date'].dt.date == start].index.tolist()[-1]

                # Add new data to current data
                ticker_df = ticker_df.append(new_ticker_df.iloc[idx + 1:], ignore_index=True)

                # Set Date column to index of DataFrame
                ticker_df.set_index(['Date'], inplace=True)

                # Save data
                ticker_df.to_csv(f'{path}{ticker}.csv')

                print(f'added {len(new_ticker_df.iloc[idx+1:].index)} records.')

            except FileNotFoundError:
                print(f'data file not found. Try to ', end='')
                self.yahoo_data_loader(ticker, path=path)
                continue

        print('='*20, 'Update finished', '='*20, '\n')
