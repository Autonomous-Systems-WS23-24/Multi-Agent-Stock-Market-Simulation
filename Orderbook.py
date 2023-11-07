import asyncio
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import spade
import talib as tl
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
import json
import warnings


class Orderbook(Agent):
    class OrderbookBehav(CyclicBehaviour):
        async def on_start(self):
            self.list_stocks = ["zoes.us.txt"]
            print("Creating Stockmarket Data . . .")
            for stock in self.list_stocks:
                self.stock_data = pd.read_csv('archive/Stocks/{}'.format(stock))
                self.stock_data = stock_cue_calc(self.stock_data)[100:102]
                print("calculation of cues completed!")

        async def run(self):
            #print("Contacting Traders")
            num_investors = 5
            self.investor_list = [f"investor{i}" for i in range(1,num_investors+1)]
            self.offerbook = pd.DataFrame(columns= ["name","buy","sell"])
            for investor in self.investor_list:
                msg = Message(to="{}@localhost".format(investor))  # Instantiate the message
                msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
                msg.body = self.stock_data.to_json(orient="split")  # Set the message content
                await self.send(msg)
            #print("Sent stockdata to traders!")

            for i in range(len(self.investor_list)):
                offers = await self.receive(timeout=10)  # wait for a message for 10 seconds
                if offers:
                    #print("Offers from Agent {} received!".format(offers.sender))
                    # print(offers.body)
                    # Specify the file path where you want to save the text file
                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore", category=FutureWarning)
                        self.dataframe_offers = pd.read_json(offers.body, orient="split")

                    #print(self.dataframe_offers)
                    self.offerbook = pd.concat([self.offerbook,self.dataframe_offers],axis=0,ignore_index=True)
                else:
                    print("Orderbook did not receive any stockdata after 10 seconds")
            await asyncio.sleep(1)
            transaction_df = self.do_transactions()
            print(self.offerbook)
            ############# now calculate new stockdata
            if not transaction_df.empty:
                self.stock_data["Close"] += transaction_df["price"].sample()
                self.stock_data["Open"] += transaction_df["price"].sample()
                self.stock_data["High"] += transaction_df["price"].max()
                self.stock_data["Low"] += transaction_df["price"].min()
            #print(transaction_df)
        def do_transactions(self):
            offerbook = self.offerbook
            df_buy_sorted = offerbook.sort_values(by="buy", ascending=False).reset_index(drop=True)
            df_sell_sorted = offerbook.sort_values(by="sell").reset_index(drop=True)
            transactions = []  # Initialize an empty list for transactions
            matched_buyers = set()
            matched_sellers = set()

            for index in range(len(df_buy_sorted.index)):
                buyer_name = df_buy_sorted["name"][index]
                seller_name = df_sell_sorted["name"][index]

                if buyer_name == seller_name:
                    continue  # Skip matching the buyer and seller with the same name

                if buyer_name not in matched_buyers and seller_name not in matched_sellers and df_buy_sorted["buy"][
                    index] >= df_sell_sorted["sell"][index]:
                    transaction_value = (df_sell_sorted["sell"][index] + df_buy_sorted["buy"][index])/2
                    transaction = {"buyer": buyer_name, "seller": seller_name, "price": transaction_value}
                    transactions.append(transaction)

                    matched_buyers.add(buyer_name)
                    matched_sellers.add(seller_name)
            # Convert the list of dictionaries into a DataFrame
                else:
                    break
            transaction_df = pd.DataFrame(transactions)

            return transaction_df
    async def setup(self):
        print("Orderbook starting . . .")
        template = Template()
        template.set_metadata("performative", "inform")
        b = self.OrderbookBehav()
        self.add_behaviour(b, template)


def stock_cue_calc(stock_data):
    # Calculate 52-day moving average
    stock_data['52-day MA'] = tl.MA(stock_data['Close'], timeperiod=52, matype=0)
    # Calculate 26-day moving average
    stock_data['26-day MA'] = tl.MA(stock_data['Close'], timeperiod=26, matype=0)
    # Calculate Relative Strength Index (RSI)
    stock_data['RSI'] = tl.RSI(stock_data['Close'], timeperiod=14)
    # Calculate Market Index and its slope
    stock_data['Market Index'] = (stock_data['High'] + stock_data['Low']) / 2
    stock_data['Market Index Slope'] = np.gradient(stock_data['Market Index'])
    # Calculate Market Level - Index Average
    market_index_average = stock_data['Market Index'].mean()
    stock_data['Market Level - Index Average'] = market_index_average
    # Calculate Market Index Acceleration
    stock_data['Market Index Acceleration'] = np.gradient(stock_data['Market Index Slope'])
    # Calculate MACD
    stock_data['MACD'], stock_data['Signal'], _ = tl.MACD(stock_data['Close'], fastperiod=12, slowperiod=26,
                                                          signalperiod=9)
    # Calcuate Stochastic Oscillator
    stock_data['K'], stock_data['D'] = tl.STOCH(stock_data['High'], stock_data['Low'], stock_data['Close'],
                                                fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3,
                                                slowd_matype=0)
    return stock_data


async def main():
    dummy = Orderbook("Orderbook@localhost", "1234")
    await dummy.start()
    print("Orderbook started. Check its console to see the output.")

    print("Wait until user interrupts with ctrl+C")
    await wait_until_finished(dummy)


if __name__ == "__main__":
    spade.run(main())
