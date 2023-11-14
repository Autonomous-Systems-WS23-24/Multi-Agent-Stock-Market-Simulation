import asyncio
import numpy as np
import spade
from spade import wait_until_finished
import Orderbook
import Investor
import Environment
import Broker

async def main():
    num_investors = 1
    num_iterations = 10
    risk_factors = np.arange(1,3.1,0.1)
    money_list = []
    stock_ownership_list = []
    stock_list = ["zoes.us.txt"]
    environment = Environment.Environment(stock_list)
    Agent_Broker = Broker.Broker("broker@localhost", "1234",environment,num_investors,stock_list,num_iterations=num_iterations)
    investors = [Investor.Investor(f"investor{i}@localhost", "1234",environment,(i%4),(i%4)*10,(i%5)*100,risk_factors[i],stock_list,num_iterations=num_iterations) for i in range(1, num_investors + 1)]
    tasks = []
    await Agent_Broker.start()
    for investor in investors:
        tasks.append(investor.start())
    await asyncio.gather(*tasks)
    print("Wait until user interrupts with ctrl+C")
    await wait_until_finished(Agent_Broker)

if __name__ == "__main__":
    spade.run(main())