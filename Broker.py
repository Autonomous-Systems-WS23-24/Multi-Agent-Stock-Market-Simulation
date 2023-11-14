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

            # end condition
            self.count += 1
            if self.count == self.agent.num_iterations:
                self.kill()

        async def receive_offers(self):
            for i in range(len(self.investor_list)):
                offers = await self.receive(timeout=10)  # wait for a message for 10 seconds
                if offers:
                    print(f"Offers from Agent {offers.sender} received!")
                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore", category=FutureWarning)
                        df_offer = pd.read_json(offers.body, orient="split")
                        # Code for adding buy offer to environment
                        if np.isnan(df_offer['sell']):
                            stock = ''
                            price = df_offer.loc[0, 'buy']
                            quantity = df_offer.loc[0, 'quantity']
                            investor_name = offers.sender
                            self.agent.environment.put_buy_offer(stock, price, quantity, investor_name)


                        elif np.isnan(df_offer['buy']):
                            stock = ''
                            price = df_offer.loc[0, 'sell']
                            quantity = df_offer.loc[0, 'quantity']
                            investor_name = offers.sender
                            self.agent.environment.put_sell_offer(stock, price, quantity, investor_name)

                        if df_offer['buy'] == np.nan and df_offer['sell'] == np.nan:
                            continue
                else:
                    print("Broker did not receive any stockdata after 10 seconds")

        async def match(self, stock):
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