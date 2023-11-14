

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



orderbook_entry = {
                    "name": [self.agent.jid[0]],
                    "sell": [sell],
                    "buy": [buy]
                }
                    self.orderbook_entry = pd.DataFrame(orderbook_entry)
                    self.orderbook_entry = pd.concat([self.orderbook_entry]*n, ignore_index=True)
                    current_networth = round(self.agent.money + self.agent.stock_count*dataframe_stockdata.at[dataframe_stockdata.index[-1], 'Close'],2)
                    asset_networth = round(self.agent.stock_count*dataframe_stockdata.at[dataframe_stockdata.index[-1], 'Close'],2)
                    #print(f"{self.agent.jid} has {current_networth} Dollars of networth")
                    self.agent.networth_list.append(current_networth)
                    self.agent.asset_networth_list.append(asset_networth)
                    self.agent.money_list.append(self.agent.money)



transactions = await self.receive(timeout=10)  # wait for a message for 10 seconds
            if transactions:
                if "no" in transactions.body:
                    pass
                else:
                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore", category=FutureWarning)
                        df_transactions = pd.read_json(transactions.body, orient="split")
                    buys = df_transactions['buyer'].str.contains(str(self.agent.jid[0]))
                    sells = df_transactions['seller'].str.contains(str(self.agent.jid[0]))
                    for price in df_transactions["price"][buys]:
                        self.agent.money -= price
                        self.agent.stock_count += 1
                    for price in df_transactions["price"][sells]:
                        self.agent.money += price
                        self.agent.stock_count -= 1


