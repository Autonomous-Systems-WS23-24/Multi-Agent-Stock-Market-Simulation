import asyncio
import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template
import random

class SimpleInvestor(Agent):
    class SimpleInvestorBehav(CyclicBehaviour):
        async def run(self):
            stockdata = await self.receive(timeout=10)  # Espera un mensaje durante 10 segundos
            if stockdata:
                print("Received stock data:")
                print(stockdata.body)
                
                # Simular una acción aleatoria (comprar o vender)
                action = random.choice(["buy", "sell"])
                print(f"Taking a random action: {action}")
                
                # Puedes enviar una confirmación al agente Orderbook
                msg = stockdata.make_reply()
                msg.body = f"Action taken: {action}"
                await self.send(msg)
            else:
                print("Did not receive any stock data after 10 seconds")

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