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
                self.stock_data = pd.read_csv('archive/Stocks/{}'.format(stock))
                self.count = 1

        async def run(self):
            self.count += 1
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
            #print(self.offerbook)
            #self.calc_new_stockdata()
            if self.count == self.agent.num_iterations:
                self.kill()



        async def send_stockdata(self):
            self.offerbook = pd.DataFrame(columns=["name", "buy", "sell"])
            for investor in self.investor_list:
                msg = Message(to="{}@localhost".format(investor))  # Instantiate the message
                msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
                msg.body = self.stock_data[101 + self.count:151 + self.count].to_json(
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
                    transaction_value = round((df_sell_sorted["sell"][index] + df_buy_sorted["buy"][index])/2)
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
                    msg.body = self.transaction_df.to_json(
                        orient="split")  # Set the message content
                    await self.send(msg)
            else:
                for investor in self.investor_list:
                    msg = Message(to="{}@localhost".format(investor))  # Instantiate the message
                    msg.set_metadata("performative", "inform")  # Set the "query" FIPA performative
                    msg.body = "--no transactions--"
                    await self.send(msg)

        def calc_new_stockdata(self):
            if not self.transaction_df.empty:
                self.stock_data["Close"] += transaction_df["price"].sample()
                self.stock_data["Open"] += transaction_df["price"].sample()
                self.stock_data["High"] += transaction_df["price"].max()
                self.stock_data["Low"] += transaction_df["price"].min()
                print(self.transaction_df)
            else:
                pass


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
