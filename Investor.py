import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template
from spade.message import Message
import Strategies
import json

class Investor(Agent):

    def __init__(self,jid,password,environment,strategy,money,risk_factor,social_weight,stock_list,time_factor,influencibility_index, num_iterations=1000):
        super().__init__(jid, password)
        self.environment = environment # environment
        self.stock_list = stock_list #list of all stocks
        # these are the attributes of an investor, we can change########################
        # this tells how much
        self.influencibility_index = round(influencibility_index,2)
        # this determines how much old data the investor looks at. maximum 100 days
        self.time_factor = round(time_factor,2)
        # number of the strategy
        self.strategy = strategy
        # how much the investor is influenced by the stock reputation vs. his own opinion
        self.social_influence = pd.DataFrame({stock: 0 for stock in self.stock_list},index=[0])
        # how easily the investor buys and sells stock
        self.risk_factor = round(risk_factor,2)
        # cash
        self.money = money
        # how important is the traders opinion in the overall reputation of the stock (weighted average)
        self.social_weight = round(social_weight,2)
        # create and normalize opinions. For the beginning this is random, the we calculate ne wones in the strategy after the first iteration
        self.opinions = pd.DataFrame({stock: np.random.rand() for stock in self.stock_list}, index=[0])
        self.opinions = self.opinions.div(self.opinions.sum(axis=1),axis=0)
        # here we define lists to keep track of the networth of every investor
        self.networth_list = []
        self.asset_networth_list = []
        self.money_list = []
        self.asset_value_lists = {}
        for stock in self.stock_list:
            self.asset_value_lists[stock]=[]
        # keep track of how many iterations to do
        self.num_iterations = num_iterations
    class InvestBehav(CyclicBehaviour):
        async def on_start(self):
            print(f"Starting {self.agent.jid} behaviour . . .")
            self.count = 0
        async def run(self):
            # give opinions of stock to other investors
            await self.socialize()
            # look at stockdata and receive orders
            await self.send_orders()
            #  update money and networth if stock was sold
            await self.ownership_update()
            self.count += 1
            if self.count == self.agent.num_iterations:
                self.kill()


        async def on_end(self):
            profit = (self.agent.networth_list[-1] - self.agent.networth_list[0])/self.agent.networth_list[0]
            self.agent.environment.get_best_investor(self.agent.jid, profit, self.agent.strategy, self.agent.risk_factor, self.agent.time_factor, self.agent.influencibility_index)
            # plot newtworth, networth distribution and relative profit
            #x = np.arange(0,len(self.agent.networth_list))
            #fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))  # 1 row, 2 columns
            #y = []
            #for stock in self.agent.stock_list:
            #    y.append(self.agent.asset_value_lists[stock])
            #y.append(self.agent.money_list)
            # total networth
            #ax1.plot(x,self.agent.networth_list,label= f"{self.agent.jid[0]} uses  strat{self.agent.strategy}, time factor {self.agent.time_factor},\n risk {self.agent.risk_factor}, influencability {self.agent.influencibility_index}")
            #ax1.set_title('networth total')
            #ax1.set_xlabel('days')
            #ax1.set_ylabel('networth')
            #ax1.legend()
            #networth distribution
            #labels = [stock for stock in self.agent.stock_list]
            #labels += ['money']
            #ax2.stackplot(x,*y, labels= labels)
            #ax2.set_title('networth distribution')
            #ax2.set_xlabel('days')
            #ax2.legend()
            #plt.tight_layout()
            #plt.show()
            #relative_change = [(day - self.agent.networth_list[0]) / self.agent.networth_list[0] for day in
             #                  self.agent.networth_list]
            #plt.plot(x, relative_change, label=f'Relative Change in Networth {self.agent.jid[0]}')
            # Add labels and title
            #plt.xlabel('Days')
            #plt.ylabel('Relative Change')
            # Show legend
            #plt.legend()
            #plt.legend()
            #plt.plot(x, relative_change, label=f'Relative Change in Networth {self.agent.jid[0]}')
            #plt.axhline(0, color='red', linestyle='--', label='y=0')
            # Add labels and title
           # plt.xlabel('Days')
          #  plt.ylabel('Relative Change')
         #   plt.show()

        async def send_orders(self):
            # sends orders to the broker
            orders = self.execute_strategy() # this function executes the strategy
            json_data = {stock: order.to_json(orient='records') for stock, order in orders.items()}
            msg = Message(to="broker@localhost")  # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.body = json.dumps(json_data)  # Set the message content
            await self.send(msg)

        def execute_strategy(self):
            # call the corresponding strategy
            strategy = f'strategy{self.agent.strategy}'
            strategy_func = getattr(Strategies, strategy, None)
            # get orders and new opinion from strategy function
            orders, new_opinion = strategy_func(self.agent.jid[0], self.agent.environment.stock_candles, self.agent.environment.stock_list, self.agent.risk_factor, self.agent.money,
                          self.agent.environment.security_register, self.agent.opinions, self.agent.social_influence, self.agent.time_factor, self.agent.influencibility_index)
            self.agent.opinions = new_opinion
            return orders

        async def ownership_update(self):
            # look if the agent sold some stock inside of the stock history, if so, send and receive money.
            conf = await self.receive(timeout=10)
            if conf:
                assets_values_total = 0
                for stock in self.agent.stock_list:
                    daily_transactions_stock = self.agent.environment.transaction_list_one_day[stock]
                    buys = daily_transactions_stock['buyer'].str.contains(str(self.agent.jid[0]))
                    sells = daily_transactions_stock['seller'].str.contains(str(self.agent.jid[0]))
                    # update money
                    for price in daily_transactions_stock["price"][buys]:
                        self.agent.money -= price
                    for price in daily_transactions_stock["price"][sells]:
                        self.agent.money += price
                    stock_high = self.agent.environment.stock_candles[stock].at[self.agent.environment.stock_candles[stock].index[-1],"High"]
                    stock_low = self.agent.environment.stock_candles[stock].at[self.agent.environment.stock_candles[stock].index[-1],"Low"]
                    stock_value = (stock_low+stock_high)/2

                    assets_values_total += stock_value*self.agent.environment.security_register.at[self.agent.jid[0],stock]
                    # all of this is for plotting
                    self.agent.asset_value_lists[stock].append(stock_value*self.agent.environment.security_register.at[self.agent.jid[0],stock])
                self.agent.asset_networth_list.append(assets_values_total)
                self.agent.money_list.append(self.agent.money)
                self.agent.networth_list.append(self.agent.money+assets_values_total)


        async def socialize(self):
            # share opinions in the stock market. Influence other investors with that
            self.agent.environment.push_opinions(self.agent.jid[0],self.agent.opinions,self.agent.social_weight)

    async def setup(self):
        print(f"{self.jid} started . . .")
        b = self.InvestBehav()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)


