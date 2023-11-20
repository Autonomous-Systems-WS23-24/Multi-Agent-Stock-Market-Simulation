import asyncio
import numpy as np
import pandas as pd
import spade
from spade import wait_until_finished
import Investor
import Environment
import Broker
import os

async def main(stock_list):
    num_investors = 20
    num_iterations = 100
    list_investors = [f"investor{i}"for i in range(1,num_investors+1)]
    data = {
        'Investor': list_investors,
        **{stock: np.random.randint(1, 101, size=len(list_investors)) for stock in stock_list}
    }
    ownership_frame = pd.DataFrame(data)
    ownership_frame.set_index("Investor", inplace=True)
    print(ownership_frame)
    risk_factors = np.arange(0,1.1,0.05)
    money_list = [i for i in range(len(stock_list))]
    environment = Environment.Environment(stock_list, ownership_frame,list_investors)
    Agent_Broker = Broker.Broker("broker@localhost", "1234",environment,num_investors,stock_list,num_iterations=num_iterations)
    investors = [Investor.Investor(f"investor{i}@localhost", "1234",environment,(i%4)+1,(i%5)*1000,risk_factors[i],1,stock_list,num_iterations=num_iterations) for i in range(1, num_investors + 1)]
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