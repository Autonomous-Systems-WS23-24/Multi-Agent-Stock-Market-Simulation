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
    Agent_Orderbook = Orderbook.Orderbook("Orderbook@localhost", "1234")
    Agent_Investor = Investor.Investor("admin@localhost", "1234")
    await Agent_Investor.start()
    await Agent_Orderbook.start()
    print("Orderbook is available. Check its console to see the output.")
    print("Wait until user interrupts with ctrl+C")
    await wait_until_finished(Agent_Orderbook)
    await wait_until_finished(Agent_Investor)




if __name__ == "__main__":
    spade.run(main())