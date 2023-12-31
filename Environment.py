import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import plotly.graph_objects as go


class Environment():
    def __init__(self, stock_list,ownership_frame,list_investors):
        self.list_investors = list_investors
        self.stock_list = stock_list
        self.security_register = ownership_frame
        # stock data registry with historical data
        self.stock_candles = {}
        self.stock_opinions = {}
        for investor in list_investors:
            self.stock_opinions[investor]= pd.DataFrame({stock: np.random.rand() for stock in self.stock_list}, index=[0])
            self.stock_opinions[investor] = self.stock_opinions[investor].div(self.stock_opinions[investor].sum(axis=1), axis=0)
        self.stock_reputation = pd.DataFrame({stock: np.random.rand() for stock in self.stock_list}, index=[0])
        self.stock_reputation = self.stock_reputation.div(self.stock_reputation.sum(axis=1), axis=0)
        self.orderbook_sell_offers = {}
        self.orderbook_buy_offers = {}
        self.transaction_list_one_day = {}
        #this part is for keeping track of statistics
        self.stock_reputation_history = []
        self.best_investor = {"jid": 1,"profit":-100}
        self.processed_investors = 0
        self.break_condition = False
        for stock in self.stock_list:
            # load historical data
            self.stock_candles[stock] = pd.read_csv('archive/Stocks/{}'.format(stock))[160:260]
            self.orderbook_sell_offers[stock] = pd.DataFrame(columns=["name", "sell"])
            self.orderbook_buy_offers[stock] = pd.DataFrame(columns=["name", "buy"])
            self.transaction_list_one_day[stock] = pd.DataFrame(columns=["buyer", "seller","price"])



    def put_buy_offer(self,stock,price,quantity,investor_name):
        for i in range(quantity):
            offer = pd.DataFrame({"name": investor_name, "buy":price}, index=[0])
            self.orderbook_buy_offers[stock] = pd.concat([self.orderbook_buy_offers[stock],offer],ignore_index=True)

    def put_sell_offer(self,stock,price,quantity,investor_name):
        for i in range(quantity):
            offer = pd.DataFrame({"name": investor_name, "sell": price}, index=[0])
            self.orderbook_sell_offers[stock] = pd.concat([self.orderbook_sell_offers[stock], offer],ignore_index=True)

    def do_transaction(self,stock,price,buyer_name,seller_name):
        # put transaction into the daily transaction list, change security register
        transaction = pd.DataFrame({"buyer": buyer_name, "seller": seller_name, "price": price}, index=[0])

        # processing transaction to update security register
        buyer = transaction["buyer"].iloc[0]
        seller = transaction["seller"].iloc[0]

        self.security_register.at[buyer, stock]  += 1
        self.security_register.at[seller, stock] -= 1

        #Update orderbook
        self.transaction_list_one_day[stock] = pd.concat([self.transaction_list_one_day[stock], transaction], ignore_index=True)
        indice_to_remove_sell = self.orderbook_sell_offers[stock][self.orderbook_sell_offers[stock]['name'].str.contains(seller_name)].head(1).index
        indice_to_remove_buy = self.orderbook_buy_offers[stock][self.orderbook_buy_offers[stock]['name'].str.contains(buyer_name)].head(1).index
        self.orderbook_buy_offers[stock].drop(indice_to_remove_buy, inplace=True)
        self.orderbook_sell_offers[stock].drop(indice_to_remove_sell, inplace=True)



    def create_candles(self):
        for stock in self.stock_list:
            # use daily transactions to create new candles
            if len(self.transaction_list_one_day[stock].index)>0:
                open = self.transaction_list_one_day[stock]["price"].iloc[-1]
                close = self.transaction_list_one_day[stock]["price"].iloc[-1]
                high = self.transaction_list_one_day[stock]["price"].max()
                low = self.transaction_list_one_day[stock]["price"].min()
                new_data = pd.DataFrame({"Close": close, "Open": open, "High": high, "Low": low}, index=[0])
                self.stock_candles[stock] = pd.concat([self.stock_candles[stock], new_data], ignore_index=True)
                self.transaction_list_one_day[stock].drop(self.transaction_list_one_day[stock].index, inplace=True)
                print(f'Today transactions happened for {stock}')

            else:
                # if there are no transactions, create artificial normally distributed transactoins, to keep the market flowing
                mean = (self.stock_candles[stock].at[self.stock_candles[stock].index[-1], "Low"] + self.stock_candles[stock].at[self.stock_candles[stock].index[-1], "High"]) / 2
                var = self.stock_candles[stock]['Close'].rolling(10).std().mean()
                random_price_data = np.random.normal(mean, var, 20)
                close = random_price_data[-1]
                open = random_price_data[0]
                low = min(random_price_data)
                high = max(random_price_data)
                new_data = pd.DataFrame({"Close": close, "Open": open, "High": high, "Low": low}, index=[0])
                self.stock_candles[stock] = pd.concat([self.stock_candles[stock], new_data], ignore_index=True)
                self.transaction_list_one_day[stock].reset_index()

    def push_opinions(self,jid,opinion,weight):
        # get the opnion of investor
        self.stock_opinions[jid] = opinion*weight

    def get_stock_reputation(self):
        # calculate the total reputation of stock
        self.stock_reputation = np.zeros(len(self.stock_list))
        for jid in self.list_investors:
            self.stock_reputation += self.stock_opinions[jid]
        self.stock_reputation = self.stock_reputation/np.sum(self.stock_reputation)
        self.stock_reputation_history.append(self.stock_reputation.tolist())

    def data_visualization(self):
        x = np.arange(0,len(self.stock_reputation_history))
        y = list(map(list, zip(*self.stock_reputation_history)))
        plt.stackplot(x, y, labels=self.stock_list)
        plt.legend()
        plt.show()

        for stock in self.stock_list:
            df = self.stock_candles[stock]
            fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                                                 open=df['Open'],
                                                 high=df['High'],
                                                 low=df['Low'],
                                                 close=df['Close'])])

            #fig.show()
    def get_best_investor(self,jid,profit,strat,risk,time,influence):
        self.processed_investors+= 1
        if profit > self.best_investor["profit"]:
            self.best_investor["jid"] = jid
            self.best_investor["profit"] = profit
            self.best_investor["strat"] = strat
            self.best_investor["risk"] = risk
            self.best_investor["time"]= time
            self.best_investor["influence"] = influence
        if self.processed_investors >= len(self.list_investors):
            print("Created file!")
            df = pd.DataFrame([self.best_investor])
            # Define the CSV file path
            csv_file_path = "best_investors.csv"
            # Check if the file already exists
            try:
                # Read the existing CSV file
                existing_df = pd.read_csv(csv_file_path)

                # Append the new data to the existing DataFrame
                updated_df = pd.concat([existing_df,df], ignore_index=True)

            except FileNotFoundError:
                # If the file doesn't exist, create a new DataFrame
                updated_df = df

            # Write the updated DataFrame to the CSV file
            updated_df.to_csv(csv_file_path, index=False)
            self.break_condition = True








