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
import Strategies_classes
import Strategies
import json


class Broker(Agent):
    def __init__(self, jid, password,environment, num_investors,stock_list, num_iterations):
        super().__init__(jid, password)
        self.stock_list = stock_list
        self.num_investors = num_investors
        self.num_iterations = num_iterations
        self.environment = environment

    class BrokerBehaviour(CyclicBehaviour):
        async def on_start(self):
            print(f"Starting Broker. . .")
            self.count = 0

        async def run(self):
            self.investor_list = [f"investor{i}" for i in range(1, self.agent.num_investors + 1)]
            await self.receive_offers()
            await self.match_transactions()

            # end condition
            self.count += 1
            if self.count == self.agent.num_iterations:
                self.kill()

        async def receive_offers(self):
            for i in range(len(self.investor_list)):
                offers = await self.receive(timeout=10)  # wait for a message for 10 seconds
                received_data = json.loads(offers.body)  # Assuming received_message is the message you received
                order_data = {stock: pd.read_json(order, orient='split') for stock, order in received_data.items()}

                if offers:
                    print(f"Offers from Agent {offers.sender} received!")
                    received_data = json.loads(offers.body)  # Assuming received_message is the message you received
                    #order_data = {stock: pd.read_json(order, orient='split') for stock, order in received_data.items()}
                    print(received_data)

                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore", category=FutureWarning)

                        for stock_data in received_data:
                            stock = list(stock_data.keys())[0]
                            order = stock_data[stock]
                            df_offer = pd.read_json(order, orient='split')

                            if np.isnan(df_offer['sell']):
                                price = df_offer.loc[0, 'buy']
                                quantity = df_offer.loc[0, 'quantity']
                                investor_name = offers.sender
                                self.agent.environment.put_buy_offer(stock, price, quantity, investor_name)


                            elif np.isnan(df_offer['buy']):
                                price = df_offer.loc[0, 'sell']
                                quantity = df_offer.loc[0, 'quantity']
                                investor_name = offers.sender
                                self.agent.environment.put_sell_offer(stock, price, quantity, investor_name)

                            if pd.isna(df_offer['buy']) and pd.isna(df_offer['sell']):
                                continue
                else:
                    print("Broker did not receive any stockdata after 10 seconds")
                    continue


        async def match_transactions(self):
            for stock in self.agent.environment.list_stocks:
                df_buy = self.agent.environment.orderbook_buy_offers[stock]
                df_sell = self.agent.environment.orderbook_sell_offers[stock]
                df_buy_sorted = df_buy.sort_values(by="buy", ascending=False).reset_index(drop=True)
                df_sell_sorted = df_sell.sort_values(by="sell").reset_index(drop=True)

                matched_buyers = set()
                matched_sellers = set()

                for index in range(len(df_buy_sorted.index)):
                    buyer_name = df_buy_sorted["name"][index]
                    seller_name = df_sell_sorted["name"][index]

                    if buyer_name == seller_name:
                        continue  # Skip matching the buyer and seller with the same name

                    if buyer_name not in matched_buyers and seller_name not in matched_sellers and df_buy_sorted["buy"][index] >= df_sell_sorted["sell"][index]:
                        price = round((df_sell_sorted["sell"][index] + df_buy_sorted["buy"][index]) / 2, 2)
                        #transaction = {"buyer": buyer_name, "seller": seller_name, "price": price}
                        self.agent.environment.do_transaction(stock, price, buyer_name, seller_name)
                        matched_buyers.add(buyer_name)
                        matched_sellers.add(seller_name)
                    # Convert the list of dictionaries into a DataFrame
                    else:
                        continue



        async def on_end(self):
            pass

    async def setup(self):
        # Add the behavior to the agent
        template = Template()
        template.set_metadata("performative", "inform")
        b = self.BrokerBehaviour()
        self.add_behaviour(b, template)
