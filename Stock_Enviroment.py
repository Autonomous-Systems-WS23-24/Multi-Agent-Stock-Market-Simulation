import asyncio
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import spade
import talib as tl
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

class Investor(Agent):
    class MyBehav(CyclicBehaviour):
        async def on_start(self):
            print("Starting behaviour . . .")
            self.money = 5000
            self.trade_condition = False
        async def run(self):
            print("I have: {} Dollars".format(self.money))
            buy_prices = calculate_buy_prices(stock_data)
            sell_prices = calculate_sell_prices(stock_data)
            orderbook_msg = [buy_prices,sell_prices]
            print("Sending Buy and Sell Offers")
            msg = Message(to="Orderbook@localhost")  # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.set_metadata("ontology", "myOntology")  # Set the ontology of the message content
            msg.set_metadata("language", "OWL-S")  # Set the language of the message content
            msg.body = orderbook_msg  # Set the message content
            await self.send(msg)

            print("Message sent!")

            # set exit_code for the behaviour
            self.exit_code = "Job Finished!"

            # stop agent from behaviour
            await self.agent.stop()
        async def calculate_buy_prices(stock_data):
            pass

        async def calculate_sell_prices(stock_data):
            pass


    async def setup(self):
        print("Agent starting . . .")
        b = self.MyBehav()
        self.add_behaviour(b)

class Stockmarket(Agent):
    class MyBehav(CyclicBehaviour):
        async def on_start(self):
            print("Starting Stock Market . . .")
            self.df = stock_cue_calc(pd.read_csv('archive/Stocks/zoes.us.txt'))
            self.counter = 0
        async def run(self):
            print("Day: {}".format(self.counter))
            self.stockprize = self.df["Open"][self.counter]
            print(self.stockprize)
            self.counter += 1
            await asyncio.sleep(1)

    async def setup(self):
        print("Agent starting . . .")
        b = self.MyBehav()
        self.add_behaviour(b)


async def main():
    dummy = Stockmarket("admin@localhost", "1234")
    await dummy.start()
    print("DummyAgent started. Check its console to see the output.")

    print("Wait until user interrupts with ctrl+C")
    await wait_until_finished(dummy)

def stock_cue_calc(stock_data):
    # Calculate 52-day moving average
    stock_data['52-day MA'] = tl.MA(stock_data['Close'], timeperiod=52, matype=0)

    # Calculate 26-day moving average
    stock_data['26-day MA'] = tl.MA(stock_data['Close'], timeperiod=26, matype=0)

    # Calculate Relative Strength Index (RSI)
    stock_data['RSI'] = tl.RSI(stock_data['Close'], timeperiod=14)

    # Calculate Market Index and its slope
    stock_data['Market Index'] = (stock_data['High'] + stock_data['Low']) / 2
    stock_data['Market Index Slope'] = np.gradient(stock_data['Market Index'])

    # Calculate Market Level - Index Average
    market_index_average = stock_data['Market Index'].mean()
    stock_data['Market Level - Index Average'] = market_index_average

    # Calculate Market Index Acceleration
    stock_data['Market Index Acceleration'] = np.gradient(stock_data['Market Index Slope'])

    # Calculate MACD
    stock_data['MACD'], stock_data['Signal'], _ = tl.MACD(stock_data['Close'], fastperiod=12, slowperiod=26,
                                                             signalperiod=9)

    # Calculate Stochastic Oscillator
    stock_data['K'], stock_data['D'] = tl.STOCH(stock_data['High'], stock_data['Low'], stock_data['Close'],
                                                   fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3,
                                                   slowd_matype=0)

    return stock_data


if __name__ == "__main__":
    #df = pd.read_csv('archive/Stocks/zoes.us.txt')
    #print(df)
    #cues = stock_cue_calc(df) # This calculates relevant quantities for technical analysis
    #plot_data = df.to_numpy()
    spade.run(main())
    #plt.plot(plot_data[:,0],plot_data[:,14]) # print some example stock
    #plt.title('Stock Price Chart')
    #plt.xlabel('Date')
    #plt.ylabel('Price')
    #print(df)
    #plt.show()