

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



