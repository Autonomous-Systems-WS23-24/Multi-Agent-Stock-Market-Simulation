import asyncio
import io

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

class Investor(Agent):
    def __init__(self, jid, password, strategy, stock, money, risk_factor, num_iterations, environment):
        super().__init__(jid, password)
        self.strategy = strategy
        self.risk_factor = risk_factor
        self.networth_list = []
        self.asset_networth_list = []
        self.money_list = []
        self.stock_count = stock
        self.money = money
        self.num_iterations = num_iterations
        environment = environment
    class InvestBehav(CyclicBehaviour):
        async def on_start(self):
            print(f"Starting {self.agent.jid} behaviour . . .")
            self.count = 0
            self.stock_list = ["1"]
        async def run(self):
            # receive stockdata
            dataframe_stockdata = self.agent.environment.stock_candles
            # use strategy and define buy and sell prices
            strategy = f'strategy{self.agent.strategy}'
            strategy_func = getattr(Strategies, strategy, None)
            buy, sell, n = strategy_func(dataframe_stockdata, self.agent.risk_factor, self.agent.money, self.agent.stock_count)
            orderbook_entry = {
                "name": [self.agent.jid[0]],
                "sell": [sell],
                "buy": [buy]
            }
            self.orderbook_entry = pd.DataFrame(orderbook_entry)
            self.orderbook_entry = pd.concat([self.orderbook_entry] * n, ignore_index=True)
            current_networth = round(self.agent.money + self.agent.stock_count * dataframe_stockdata.at[
                dataframe_stockdata.index[-1], 'Close'], 2)
            asset_networth = round(
            self.agent.stock_count * dataframe_stockdata.at[dataframe_stockdata.index[-1], 'Close'], 2)
            # print(f"{self.agent.jid} has {current_networth} Dollars of networth")
            self.agent.networth_list.append(current_networth)
            self.agent.asset_networth_list.append(asset_networth)
            self.agent.money_list.append(self.agent.money)

            # end statement
            self.count += 1
            if self.count == self.agent.num_iterations:
                self.kill()

        async def on_end(self):
            x = np.arange(0,len(self.agent.networth_list))

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))  # 1 row, 2 columns
            # total networth
            ax1.plot(x,self.agent.networth_list,label= f"Networth of {self.agent.jid[0]}")
            ax1.set_title('networth total')
            ax1.set_xlabel('days')
            ax1.set_ylabel('networth')
            ax1.legend()
            # networth distribution
            ax2.stackplot(x,self.agent.money_list,self.agent.asset_networth_list, labels= ["money","stock assets"])
            ax2.set_title('networth distribution')
            ax2.set_xlabel('days')
            ax2.legend()
            plt.tight_layout()
            plt.show()

        async def orderbook_send(self):
            print(f" Investor{self.agent.jid} Sending Buy and Sell Offers to The orderbook ")
            msg = Message(to="Orderbook@localhost")  # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.set_metadata("ontology", "myOntology")  # Set the ontology of the message content
            msg.set_metadata("language", "OWL-S")  # Set the language of the message content
            msg.body = self.orderbook_entry.to_json(orient="split")  # Set the message content
            await self.send(msg)

        async def transactions_process(self):
            transactions = await self.receive(timeout=10)  # wait for a message for 10 seconds
            if transactions:
                if "no" in transactions.body:
                    pass
                else:
                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore", category=FutureWarning)
                        df_transactions = pd.read_json(transactions.body, orient="split")
                    buys = df_transactions['buyer'].str.contains(str(self.agent.jid[0]))
                    sells = df_transactions['seller'].str.contains(str(self.agent.jid[0]))
                    for price in df_transactions["price"][buys]:
                        self.agent.money -= price
                        self.agent.stock_count += 1
                    for price in df_transactions["price"][sells]:
                        self.agent.money += price
                        self.agent.stock_count -= 1
    async def setup(self):
        print(f"{self.jid} started . . .")
        b = self.InvestBehav()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)


