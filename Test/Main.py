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
import Orderbook
import Orderbook_historical_data
import Investor
import Environment
import Broker



async def main():
    num_investors = 2
    num_iterations = 100
    risk_factors = np.arange(1,3.1,0.1)
    money_list = []
    list_stocks = ["zoes.us.txt"]
    environment = Environment(list_stocks)
    Broker = Broker.Broker("Broker@localhost", "1234", num_investors, num_iterations=num_iterations, environment=environment)
    investors = [Investor.Investor(f"investor{i}@localhost", "1234",(i%4)+1,(i%4)*10,(i%5)*100,risk_factors[i],num_iterations=num_iterations, environment=environment) for i in range(1, num_investors + 1)]
    tasks = []
    for investor in investors:
        tasks.append(investor.start())
    await asyncio.gather(*tasks)
    await Broker.start()
    print("Wait until user interrupts with ctrl+C")
    #Broker.web.start(hostname="127.0.0.1", port="10000")
    tasks = []
    await wait_until_finished(Broker)
    for investor in investors:
        tasks.append(wait_until_finished(investor))
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    spade.run(main())