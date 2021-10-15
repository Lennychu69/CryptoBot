import cbpro, json, time, calendar, math, datetime


# import matplotlib.pyplot as plt

class kraberBot():

    def __init__(self, client, currency):
        # TODO Add more of these if needed
        self.authClient = client
        self.currency = currency
        self.coin_account = None
        self.USD_account = None
        self.fee = .005  # Decimal of 0.5%
        self.last_buy_price = -1
        # self.seen_prices = []

        for account in self.authClient.get_accounts():
            if account["currency"] == self.currency:
                self.coin_account = account
            if account["currency"] == "USD":
                self.USD_account = account

        self.balance = self.USD_account["balance"]
        self.coin_balance = self.coin_account["balance"]

    # need buy function (USD->Currency) (True means amount is in coin, false means in USD)
    def buy(self, amount, exchangeTypeFlag):
        p_id = self.currency + "-USD"
        if (exchangeTypeFlag):
            self.authClient.buy(size=amount, product_id=p_id, order_type="market")
            print("Successfully bought " + str(amount) + " of " + self.currency)  # add at price
        else:
            self.authClient.buy(funds=amount, product_id=p_id, order_type="market")
            print("Successfully bought " + str(amount) + "$ worth of " + self.currency)  # add at price

    # need sell function (Currency->USD)
    def sell(self, amount, exchangeTypeFlag):
        p_id = self.currency + "-USD"
        if (exchangeTypeFlag):
            self.authClient.sell(size=amount, product_id=p_id, order_type="market")
            print("Successfully sold " + str(amount) + " of " + self.currency)  # add at price
        else:
            self.authClient.sell(funds=amount, product_id=p_id, order_type="market")
            print("Successfully sold " + str(amount) + "$ worth of " + self.currency)  # add at price

    def updateBalances(self):
        self.balance = self.USD_account["balance"]
        self.coin_balance = self.coin_account["balance"]

    # def getCurrentPrice(self):
    #    price = self.authClient.get_product_ticker(product_id=(self.currency + "-USD"))["price"]
    #    return price

    def printBalances(self):
        print("USD Balance: " + str(self.balance))
        print("Coin Balance: " + str(self.coin_balance))

    def getHistoricData(self, cycles):
        current_time = datetime.datetime.now()
        gran = 60
        time_offset = gran * 300
        historic_times = []
        historic_price = []

        for i in range(cycles):
            s = (current_time - datetime.timedelta(seconds=time_offset * (i + 1)))
            e = (current_time - datetime.timedelta(seconds=time_offset * i))
            historic_data = self.authClient.get_product_historic_rates((self.currency + "-USD"), start=s, end=e,granularity=gran)
            for x in historic_data:
                historic_times.insert(0, x[0])
                historic_price.insert(0, x[1])

        return historic_price

    # def addSeenPrice(self):
    #    self.seen_prices.append(self.getCurrentPrice())

    # Given an array of data, take the moving average of a length of the with the most recent elements
    def calcMovingAvg(self, data, length):
        l = length
        if len(data) == 0:
            return 0.0
        elif len(data) <= l:
            t = data
        else:
            t = data[-l:]
        avg = 0
        # print(t)
        for datapt in t:
            avg += datapt
        avg = avg / len(t)
        return avg

    # Should be passing in a Moving Average Array, not raw data
    # Will return either "Growth", "Decline" or "Stable" and then the average slope
    def calcTrendDirection(self, data, length):
        l = length
        if len(data) == 0:
            return ["Stable", 0.0]
        elif len(data) <= l:
            t = data
        else:
            t = data[-l:]

        average_slope = 0

        for data_num in range(len(t)):
            if (data_num != 0):
                slope = t[data_num] - t[data_num-1]
                average_slope += slope

        # This is ugly but what do i do. Makes it so you don't  divide by 0 and brick
        try:
            average_slope /= (len(t)-1)
        except:
            average_slope = average_slope

        if(average_slope >= 0):
            return ["Growth", average_slope]
        else:
            return ["Decline", average_slope]

    # TODO Figure out thoughtCycle because it suck
    def thoughtCycle(self, growth_array, mv_a_array):
        self.updateBalances()
        if(len(mv_a_array)<=200):
            return "Waiting, still calibrating trends."



        # determines buy, sell, or wait
        # TODO This will need parameters and might get finalized using ML
        # Growth, Stability, Decline - DONE!
        # I lose money on trades where I've made less than 1%

        # buy when:
            # growth of more than x%
        # sell when:
            # price goes y% under buy price
            # price dips below z% of max price seen
            # price has been in decline of >a% for b ticks

        return None

