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
    def __init__(self, jid, password, num_investors, num_iterations):
        super().__init__(jid, password)
        self.num_investors = num_investors
        self.num_iterations = num_iterations
    class BrokerBehaviour(CyclicBehaviour):
            async def on_start(self):
                print(f"Starting Broker. . .")
                self.count = 0
            async def run(self):
                self.investor_list = [f"investor{i}" for i in range(1, self.agent.num_investors + 1)]

                #end condition
                self.count += 1
                if self.count == self.agent.num_iterations:
                    self.kill()



            async def receive_offers(self):
                for i in range(len(self.investor_list)):
                    offers = await self.receive(timeout=10)  # wait for a message for 10 seconds
                    if offers:
                        print(f"Offers from Agent {offers.sender} received!")
                        print(offers.body)
                        with warnings.catch_warnings():
                            warnings.filterwarnings("ignore", category=FutureWarning)
                            df_offer = pd.read_json(offers.body, orient="split")
                            #Code for adding buy offer to environment
                            if df_offer['sell'] == np.nan:
                                stock = ''
                                price = df_offer.loc[0, 'buy']
                                quantity = df_offer.loc[0, 'quantity']
                                investor_name = offers.sender
                                self.agent.environment.put_buy_offer(stock ,price, quantity, investor_name)

                            if df_offer['buy'] == np.nan:
                                stock = ''
                                price = df_offer.loc[0,'sell']
                                quantity = df_offer.loc[0, 'quantity']
                                investor_name = offers.sender
                                self.agent.environment.put_sell_offer(stock ,price, quantity, investor_name)

                            if df_offer['buy'] == np.nan and df_offer['sell'] == np.nan:
                                pass
                    else:
                        print("Broker did not receive any stockdata after 10 seconds")

            async def on_end(self):
                pass

    async def setup(self):
        # Add the behavior to the agent
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(BrokerBehaviour(), template)
