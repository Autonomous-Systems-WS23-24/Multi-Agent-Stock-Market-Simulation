import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template
from spade.message import Message
import warnings
import json


class Broker(Agent):
    def __init__(self, jid, password,environment, num_investors,stock_list, num_iterations):
        super().__init__(jid, password)
        # give initialization values
        self.stock_list = stock_list
        self.num_investors = num_investors
        self.num_iterations = num_iterations
        self.environment = environment
        self.investor_list = [f"investor{i}" for i in range(1, self.num_investors + 1)]

    class BrokerBehaviour(CyclicBehaviour):
        async def on_start(self):
            print(f"Starting Broker. . .")
            self.count = 0
            # keep track of iterations


        async def run(self):
            # wait for Investors to contact broker and send offers
            await self.receive_offers()
            # match the matching offers and do the transactions. this acts on the environment
            await self.match_transactions()
            # end condition
            self.count += 1
            print(f'Currenly on day {self.count}!')
            if self.count == self.agent.num_iterations:
                self.kill()

        async def receive_offers(self):
            # wait for all investors to send msg
            for i in range(len(self.agent.investor_list)):
                offers = await self.receive(timeout=10)  # wait for a message for 10 seconds

                if offers:
                    received_data = json.loads(offers.body)
                    order_data = {stock: order for stock, order in received_data.items()}

                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore", category=FutureWarning)

                        for stock, order in order_data.items():

                            df_offer = pd.read_json(order, orient='records')
                            # check if offer is buy or sell offer, then put it in the correspondiing list
                            if np.isnan(df_offer.loc[0,'sell']) and not np.isnan(df_offer.loc[0,'buy']):
                                price = df_offer.loc[0, 'buy']
                                quantity = df_offer.loc[0, 'quantity']
                                investor_name = offers.sender[0]
                                self.agent.environment.put_buy_offer(stock, price, quantity, investor_name)
                            # check if offer is buy or sell offer, then put it in the correspondiing list
                            elif np.isnan(df_offer.loc[0,'buy']) and not np.isnan(df_offer.loc[0,'sell']):
                                price = df_offer.loc[0, 'sell']
                                quantity = df_offer.loc[0, 'quantity']
                                investor_name = offers.sender[0]
                                # safety-check if the trader actually has the stock
                                if self.agent.environment.security_register.at[investor_name, stock] >= quantity:
                                    self.agent.environment.put_sell_offer(stock, price, quantity, investor_name)
                            else:
                                continue
                else:
                    print("Broker did not receive any offers after 10 seconds")
                    continue


        async def match_transactions(self):
            # Create new stock candles from Transactions of the last day
            self.agent.environment.create_candles()
            # look at all the stocks and match the offers
            for stock in self.agent.environment.stock_list:
                # sort by prize
                df_buy = self.agent.environment.orderbook_buy_offers[stock]
                df_sell = self.agent.environment.orderbook_sell_offers[stock]
                df_buy_sorted = df_buy.sort_values(by="buy", ascending=False).reset_index(drop=True)
                df_sell_sorted = df_sell.sort_values(by="sell").reset_index(drop=True)

                # iterate
                for index in range(min(len(df_buy_sorted.index),len(df_sell_sorted))):
                    buyer_name = df_buy_sorted["name"][index]
                    seller_name = df_sell_sorted["name"][index]
                    # Double check if seller has the stock
                    if df_buy_sorted["buy"][index] >= df_sell_sorted["sell"][index] and self.agent.environment.security_register.at[seller_name, stock] >= 1:

                        #transaction = {"buyer": buyer_name, "seller": seller_name, "price": price}
                        price = round((df_sell_sorted["sell"][index] + df_buy_sorted["buy"][index]) / 2, 2)
                        self.agent.environment.do_transaction(stock, price, buyer_name, seller_name)
                    # break at the first pair which doesnt match
                    else: break
            # Update the reputation  of the stock
            self.agent.environment.get_stock_reputation()

            # clear the not matched transactions
            for stock in self.agent.environment.stock_list:
                # Remove old offers that have not been matched
                self.agent.environment.orderbook_buy_offers[stock].drop(self.agent.environment.orderbook_buy_offers[stock].index, inplace=True)
                self.agent.environment.orderbook_sell_offers[stock].drop(self.agent.environment.orderbook_sell_offers[stock].index, inplace=True)

            # send confirm to investors
            for investor in range(1, self.agent.num_investors + 1):
                msg = Message(to="investor{}@localhost".format(investor))
                msg.set_metadata("performative", "inform")
                msg.body = "--transactions_done--"
                await self.send(msg)

        async def on_end(self):
            print('Broker finished iterations')
            # plot stock data
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
