import asyncio
import numpy as np
import pandas as pd
import spade
from spade import wait_until_finished
import Investor
import Environment
import Broker
import os
import random

async def main(num_investors,num_iterations):
    # find where the stockdata is, create list
    package_dir = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(package_dir, 'archive/Stocks')
    stock_list = os.listdir(data_directory)

    # create list of investors
    list_investors = [f"investor{i}"for i in range(1,num_investors+1)]
    data = {
        'Investor': list_investors,
        **{stock: np.random.randint(1, 101, size=len(list_investors)) for stock in stock_list}
    }

    # give investors stock possessions randomly on a count between 0 and 100
    ownership_frame = pd.DataFrame(data)
    ownership_frame.set_index("Investor", inplace=True)
    print(ownership_frame)

    # initialize agent properties
    money_list = [i for i in range(len(stock_list))]

    # initialize agents and environment
    environment = Environment.Environment(stock_list, ownership_frame,list_investors)
    Agent_Broker = Broker.Broker("broker@localhost", "1234",environment,num_investors,stock_list,num_iterations=num_iterations)
    investors = [Investor.Investor(f"investor{i}@localhost", "1234",environment,(i%4)+1,(i%5)*1000,random.uniform(0, 1),1,stock_list,random.uniform(0.2, 1),random.uniform(0.5,1),num_iterations=num_iterations) for i in range(1, num_investors + 1)]
    tasks = []
    await Agent_Broker.start()
    for investor in investors:
        tasks.append(investor.start())
    await asyncio.gather(*tasks)
    print("Wait until user interrupts with ctrl+C")
    await wait_until_finished(Agent_Broker)

if __name__ == "__main__":
    num_investors = 20
    num_iterations = 100
    spade.run(main(num_investors,num_iterations))