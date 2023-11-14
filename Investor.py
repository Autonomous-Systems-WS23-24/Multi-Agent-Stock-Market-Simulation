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
import json

class Investor(Agent):

    def __init__(self,jid,password,environment,strategy,stock,money,risk_factor,stock_list,num_iterations=1000):
        super().__init__(jid, password)
        self.environment = environment
        self.stock_list = stock_list
        self.strategy = strategy
        self.diversification_factor = 1
        self.social_influence = pd.DataFrame(columns=self.stock_list)
        self.opinions = pd.DataFrame(columns= self.stock_list)
        self.risk_factor = risk_factor
        self.networth_list = []
        self.asset_networth_list = []
        self.money_list = []
        self.stock_count = stock
        self.money = money
        self.num_iterations = num_iterations
    class InvestBehav(CyclicBehaviour):
        async def on_start(self):
            print(f"Starting {self.agent.jid} behaviour . . .")
            self.count = 0
        async def run(self):
            # look at stockdata and receive orders
            await self.send_orders()
            # look if you sold some stock
            await self.ownership_update()
            # receive transactions done
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

        async def send_orders(self):
            stockdata = self.agent.environment.stock_candles  # wait for a message for 10 seconds
            # instantiate strategy using strategy_num by setting it manually
            strategy = f'strategy{self.agent.strategy}'
            strategy_func = getattr(Strategies, strategy, None)
            orders = strategy_func(stockdata,self.agent.environment.list_stocks,self.agent.risk_factor,self.agent.money,self.agent.stock_count,self.agent.opinions,self.agent.social_influence)
            json_data = {stock: order.to_json(orient='records') for stock, order in orders.items()}
            msg = Message(to="broker@localhost")  # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.body = json.dumps(json_data)  # Set the message content
            await self.send(msg)

        async def ownership_update(self):
            for stock in self.agent.stock_list:
                daily_transactions_stock = self.agent.environment.transaction_list_one_day[stock]
                buys = daily_transactions_stock['buyer'].str.contains(str(self.agent.jid[0]))
                sells = daily_transactions_stock['seller'].str.contains(str(self.agent.jid[0]))
                for price in daily_transactions_stock["price"][buys]:
                    self.agent.money -= price
                    self.agent.stock_count[stock] += 1
                for price in daily_transactions_stock["price"][sells]:
                    self.agent.money += price
                    self.agent.stock_count[stock] -= 1
        async def socialize(self):
            for investor in self.agent.investor_list:
                msg = Message(to="{}@localhost".format(investor))  # Instantiate the message
                msg.set_metadata("performative", "inform")  # Set the "query" FIPA performative
                msg.body = self.agent.opinions.to_json(orient="split")  # Set the message content
                await self.send(msg)
            for investor in self.agent.investor_list:
                pass


    async def setup(self):
        print(f"{self.jid} started . . .")
        b = self.InvestBehav()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)


