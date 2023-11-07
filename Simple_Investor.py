import asyncio
import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template
import random

class SimpleInvestor(Agent):
    class SimpleInvestorBehav(CyclicBehaviour):
        async def run(self):
            stockdata = await self.receive(timeout=10)  # Should it recieve any info? Maybe for the randomness in buy_prices and sell_prices
            if stockdata:
                print("Received stock data:")
                print(stockdata.body)
                

                buy_prices=random.random(stockdata)
                sell_prices=random.random(stockdata)

                # Simulate a random action (buy or sell)
                action = random.choice(["buy", "sell"])
                print(f"Taking a random action: {action}")
                

                if action=="buy":
                    pass
                elif action=="sell":
                    pass



                # Send a confirmation to Orderbook agent
                msg = stockdata.make_reply()
                msg.body = f"Action taken: {action}"
                await self.send(msg)
            else:
                print("Did not receive any stock data after 10 seconds")
                self.kill()

    async def setup(self):
        print("SimpleInvestor started")
        b = self.SimpleInvestorBehav()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)

async def main():
    simple_investor = SimpleInvestor("simple_investor@localhost", "1234")
    await simple_investor.start()
    print("SimpleInvestor is available. Check its console to see the output.")
    print("Wait until user interrupts with ctrl+C")

if __name__ == "__main__":
    spade.run(main())