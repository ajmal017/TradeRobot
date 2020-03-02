class Schedule:
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