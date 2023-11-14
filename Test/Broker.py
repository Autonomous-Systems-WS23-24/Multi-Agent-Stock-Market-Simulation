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

    async def setup(self):
        # Define a behavior to interact with the environment and air traffic control
        class BrokerBehaviour(CyclicBehaviour):
            async def on_start(self):
                print(f"Starting Broker. . .")
                self.count = 0
            async def run(self):
                self.investor_list = [f"investor{i}" for i in range(1, self.agent.num_investors + 1)]


                await self.send_instruction_to_atc(aircraft_position)

            async def send_instruction_to_atc(self, position):
                # Create an ACL message to send data to the air traffic control agent
                msg = Message(to="atc_agent@localhost")  # Replace with the correct ATC agent JID
                msg.set_metadata("performative", "inform")
                msg.body = f"Aircraft at position {position} requesting instructions."

                # Send the message
                await self.send(msg)

            async def receive_offers(self):
                for i in range(len(self.investor_list)):
                    offers = await self.receive(timeout=10)  # wait for a message for 10 seconds
                    if offers:
                        print(f"Offers from Agent {offers.sender} received!")
                        print(offers.body)
                        with warnings.catch_warnings():
                            warnings.filterwarnings("ignore", category=FutureWarning)
                            self.dataframe_offers = pd.read_json(offers.body, orient="split")
                            self.offerbook = pd.concat([self.offerbook, self.dataframe_offers], axis=0,
                                                       ignore_index=True)

                    else:
                        print("Broker did not receive any stockdata after 10 seconds")

            async def on_end(self):
                pass


        # Add the behavior to the agent
        self.add_behaviour(BrokerBehaviour())