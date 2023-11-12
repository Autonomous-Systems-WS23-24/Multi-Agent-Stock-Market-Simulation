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
import Investor


async def main():
    num_investors = 20
    num_iterations = 1000
    risk_factors = np.arange(1,3.1,0.1)
    Agent_Orderbook = Orderbook.Orderbook("Orderbook@localhost", "1234",num_investors,num_iterations=num_iterations)
    investors = [Investor.Investor(f"investor{i}@localhost", "1234",(i%4)+1,risk_factors[i],num_iterations=num_iterations) for i in range(1, num_investors + 1)]
    tasks = []
    for investor in investors:
        tasks.append(investor.start())
    await asyncio.gather(*tasks)
    await Agent_Orderbook.start()
    print("Wait until user interrupts with ctrl+C")
    Agent_Orderbook.web.start(hostname="127.0.0.1", port="10000")
    await wait_until_finished(Agent_Orderbook)


if __name__ == "__main__":
    spade.run(main())