import asyncio
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import spade
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
import json
import warnings
import random as rd


class Orderbook(Agent):

    def __init__(self,jid,password,num_investors,num_iterations=1000):
        super().__init__(jid, password)
        self.num_investors= num_investors
        self.num_iterations = num_iterations
    class OrderbookBehav(CyclicBehaviour):
        async def on_start(self):
            self.list_stocks = ["zoes.us.txt"]
            print("Creating Stockmarket Data . . .")
            for stock in self.list_stocks:
                self.stock_data_history = pd.read_csv('archive/Stocks/{}'.format(stock))
                self.stock_data = self.stock_data_history[10:60]
                self.count = 0

        async def run(self):
            self.investor_list = [f"investor{i}" for i in range(1,self.agent.num_investors+1)]
            #  send data to traders
            await self.send_stockdata()
            # receive their offers
            await self.receive_offers()
            # wait one second for each iteration for trader calculation
            #await asyncio.sleep(0.1)
            # do transactions
            self.do_transactions()
            # send transaction data
            await self.send_transactions()
            self.count += 1
            if self.count == self.agent.num_iterations:
                self.kill()
            #print(self.offerbook)
            self.calc_new_stockdata()


        async def on_end(self):
            x = np.arange(0, len(self.stock_data["Close"].to_list()))
            y = self.stock_data["Close"].to_list()
            plt.xlabel("days")
            plt.ylabel("value")
            plt.plot(x,y, label=f"Stock value")
            plt.ylim(0, max(y) * 1.1)
            plt.legend()
            plt.show()


        async def send_stockdata(self):
            self.offerbook = pd.DataFrame(columns=["name", "buy", "sell"])
            for investor in self.investor_list:
                msg = Message(to="{}@localhost".format(investor))  # Instantiate the message
                msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
                msg.body = self.stock_data.to_json(
                    orient="split")  # Set the message content
                await self.send(msg)

        async def receive_offers(self):
            for i in range(len(self.investor_list)):
                offers = await self.receive(timeout=10)  # wait for a message for 10 seconds
                if offers:
                    #print("Offers from Agent {} received!".format(offers.sender))
                    # print(offers.body)
                    # Specify the file path where you want to save the text file
                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore", category=FutureWarning)
                        self.dataframe_offers = pd.read_json(offers.body, orient="split")
                        self.offerbook = pd.concat([self.offerbook, self.dataframe_offers], axis=0, ignore_index=True)

                else:
                    print("Orderbook did not receive any stockdata after 10 seconds")

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
                    transaction_value = round((df_sell_sorted["sell"][index] + df_buy_sorted["buy"][index])/2,2)
                    transaction = {"buyer": buyer_name, "seller": seller_name, "price": transaction_value}
                    transactions.append(transaction)

                    matched_buyers.add(buyer_name)
                    matched_sellers.add(seller_name)
            # Convert the list of dictionaries into a DataFrame
                else:
                    break
            self.transaction_df = pd.DataFrame(transactions)


        async def send_transactions(self):
            if not self.transaction_df.empty:
                for investor in self.investor_list:
                    msg = Message(to="{}@localhost".format(investor))  # Instantiate the message
                    msg.set_metadata("performative", "inform")  # Set the "query" FIPA performative
                    msg.body = self.transaction_df.to_json(orient="split")  # Set the message content
                    await self.send(msg)
            else:
                for investor in self.investor_list:
                    msg = Message(to="{}@localhost".format(investor))  # Instantiate the message
                    msg.set_metadata("performative", "inform")  # Set the "query" FIPA performative
                    msg.body = "--no transactions--"
                    await self.send(msg)

        def calc_new_stockdata(self):
            if not self.transaction_df.empty:
                print("Transactions!")
                close = rd.choice(self.transaction_df["price"].tolist())
                open = rd.choice(self.transaction_df["price"].tolist())
                low = self.transaction_df["price"].min()*rd.randrange(90,100)/100
                high = (self.transaction_df["price"].max()*rd.randrange(100,110))/100
                new_data = pd.DataFrame({"Close":close,"Open":open,"High": high,"Low":low},index=[0])
                self.stock_data = pd.concat([self.stock_data,new_data],ignore_index=True)

            else:
                print("No transactions! Creating artificial Data!")
                mean = (self.stock_data.at[self.stock_data.index[-1],"Low"]+ self.stock_data.at[self.stock_data.index[-1],"High"])/2
                var = self.stock_data['Close'].rolling(10).std().mean()
                random_price_data = np.random.normal(mean,var,20)
                close = random_price_data[-1]
                open = random_price_data[0]
                low = random_price_data.min()
                high = random_price_data.max()
                new_data = pd.DataFrame({"Close": close, "Open": open, "High": high, "Low": low},index=[0])
                self.stock_data = pd.concat([self.stock_data, new_data],ignore_index=True)
    async def setup(self):
        print("Orderbook starting . . .")
        template = Template()
        template.set_metadata("performative", "inform")
        b = self.OrderbookBehav()
        self.add_behaviour(b, template)



async def main():
    dummy = Orderbook("Orderbook@localhost", "1234")
    await dummy.start()
    print("Orderbook started. Check its console to see the output.")

    print("Wait until user interrupts with ctrl+C")
    await wait_until_finished(dummy)


if __name__ == "__main__":
    spade.run(main())
