import asyncio

import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import spade
import talib as tl
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template
from spade.message import Message
import warnings
import Strategies
import json


class Broker(Agent):
    def __init__(self, jid, password,environment, num_investors,stock_list, num_iterations):
        super().__init__(jid, password)
        self.stock_list = stock_list
        self.num_investors = num_investors
        self.num_iterations = num_iterations
        self.environment = environment
        self.investor_list = [f"investor{i}" for i in range(1, self.num_investors + 1)]

    class BrokerBehaviour(CyclicBehaviour):
        async def on_start(self):
            print(f"Starting Broker. . .")
            self.count = 0
            # to giuve the investors time to start
            await asyncio.sleep(3)

        async def run(self):
            await self.receive_offers()
            await self.match_transactions()
            # end condition
            self.count += 1
            if self.count == self.agent.num_iterations:
                self.kill()

        async def receive_offers(self):
            for i in range(len(self.agent.investor_list)):
                offers = await self.receive(timeout=10)  # wait for a message for 10 seconds

                if offers:
                    received_data = json.loads(offers.body)  # Assuming received_message is the message you received
                    order_data = {stock: order for stock, order in received_data.items()}
                    #print(received_data)

                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore", category=FutureWarning)

                        for stock, order in order_data.items():

                            df_offer = pd.read_json(order, orient='records')
                            #print(df_offer)

                            if np.isnan(df_offer.loc[0,'sell']) and not np.isnan(df_offer.loc[0,'buy']):
                                price = df_offer.loc[0, 'buy']
                                quantity = df_offer.loc[0, 'quantity']
                                investor_name = offers.sender[0]
                                self.agent.environment.put_buy_offer(stock, price, quantity, investor_name)

                            elif np.isnan(df_offer.loc[0,'buy']) and not np.isnan(df_offer.loc[0,'sell']):
                                price = df_offer.loc[0, 'sell']
                                quantity = df_offer.loc[0, 'quantity']
                                investor_name = offers.sender[0]
                                if self.agent.environment.security_register.at[investor_name, stock] >= quantity:
                                    self.agent.environment.put_sell_offer(stock, price, quantity, investor_name)

                            else:
                                continue
                else:
                    print("Broker did not receive any offers after 10 seconds")
                    continue


        async def match_transactions(self):
            for stock in self.agent.environment.stock_list:
                df_buy = self.agent.environment.orderbook_buy_offers[stock]
                df_sell = self.agent.environment.orderbook_sell_offers[stock]
                df_buy_sorted = df_buy.sort_values(by="buy", ascending=False).reset_index(drop=True)
                df_sell_sorted = df_sell.sort_values(by="sell").reset_index(drop=True)


                for index in range(min(len(df_buy_sorted.index),len(df_sell_sorted))):
                    buyer_name = df_buy_sorted["name"][index]
                    seller_name = df_sell_sorted["name"][index]
                    # Double check if seller has the stock
                    if df_buy_sorted["buy"][index] >= df_sell_sorted["sell"][index] and self.agent.environment.security_register.at[seller_name, stock] >= 1:

                        #transaction = {"buyer": buyer_name, "seller": seller_name, "price": price}
                        price = round((df_sell_sorted["sell"][index] + df_buy_sorted["buy"][index]) / 2, 2)

                        self.agent.environment.do_transaction(stock, price, buyer_name, seller_name)

            # Create new stock candles from Transactions
            self.agent.environment.create_candles()
            # Update the reputation  of the stock
            try:
                self.agent.environment.get_stock_reputation()
            except: pass

            for stock in self.agent.environment.stock_list:
                # Remove old offers that have not been matched
                self.agent.environment.orderbook_buy_offers[stock].drop(self.agent.environment.orderbook_buy_offers[stock].index, inplace=True)
                self.agent.environment.orderbook_sell_offers[stock].drop(self.agent.environment.orderbook_sell_offers[stock].index, inplace=True)


            for investor in range(1, self.agent.num_investors + 1):
                msg = Message(to="investor{}@localhost".format(investor))  # Instantiate the message
                msg.set_metadata("performative", "inform")  # Set the "query" FIPA performative
                msg.body = "--transactions_done--"
                await self.send(msg)

        async def on_end(self):
            print('Broker finished iterations')
            #print(self.agent.environment.security_register)
            for stock in self.agent.stock_list:
                x = np.arange(0, len(self.agent.environment.stock_candles[stock]["Close"].to_list()))
                y = self.agent.environment.stock_candles[stock]["Close"].to_list()
                plt.xlabel("days")
                plt.ylabel("value")
                plt.plot(x, y, label=f"Stock {stock} candles")
                plt.ylim(0, max(y) * 1.1)
                plt.legend()
                plt.show()

            self.agent.environment.data_visualization()

    async def setup(self):
        # Add the behavior to the agent
        template = Template()
        template.set_metadata("performative", "inform")
        b = self.BrokerBehaviour()
        self.add_behaviour(b, template)
