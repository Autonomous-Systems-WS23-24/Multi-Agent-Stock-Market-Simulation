import asyncio
import numpy as np
import spade
from spade import wait_until_finished
import Orderbook
import Investor
import Environment
import Broker
import os

async def main(stock_list):
    num_investors = 10
    num_iterations = 1000
    risk_factors = np.arange(1,3.1,0.1)
    money_list = [i for i in range(len(stock_list))]
    stock_ownership_list = []
    environment = Environment.Environment(stock_list,num_investors)
    Agent_Broker = Broker.Broker("broker@localhost", "1234",environment,num_investors,stock_list,num_iterations=num_iterations)
    investors = [Investor.Investor(f"investor{i}@localhost", "1234",environment,1,(i%4)*10,(i%5)*100,risk_factors[i],stock_list,num_iterations=num_iterations) for i in range(1, num_investors + 1)]
    tasks = []
    await Agent_Broker.start()
    for investor in investors:
        tasks.append(investor.start())
    await asyncio.gather(*tasks)
    print("Wait until user interrupts with ctrl+C")
    await wait_until_finished(Agent_Broker)

if __name__ == "__main__":
    package_dir = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(package_dir, 'archive/Stocks')
    stock_list = os.listdir(data_directory)
    spade.run(main(stock_list))