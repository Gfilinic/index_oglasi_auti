import asyncio
import spade
import json
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

from scraping import IndexScraper
from databaseAgent import DatabaseAgent

class TopLevelAgent(Agent):
    class PeriodicTaskBehaviour(CyclicBehaviour):
        async def on_start(self):
            print("Starting behaviour . . .")
            self.counter = 0
            self.scraper_initialized = False

        async def run(self):
            print("Counter: {}".format(self.counter))
            self.counter += 1

            await self.initialize_scraper()

            data = self.scraper.sort_data()
            comparison_task = asyncio.create_task(self.start_database_agent(data))
            await asyncio.gather(comparison_task)
            await asyncio.sleep(6000)

        async def start_database_agent(self, data):
            database_agent = DatabaseAgent("database@localhost", "db")
            await database_agent.start()
            message = spade.message.Message(to=str(database_agent.jid))
            message.body = json.dumps(data)
            await self.send(message)

        async def initialize_scraper(self):
            self.scraper = IndexScraper()
            

    async def setup(self):
        print(f"Top-level agent {self.jid} is starting...")
        b = self.PeriodicTaskBehaviour()
        self.add_behaviour(b)

async def main():
    top_agent = TopLevelAgent("post@localhost", "main")
    await top_agent.start()
    print("Top agent started. Check its console to see the output.")

    print("Wait until user interrupts with ctrl+C")
    await wait_until_finished(top_agent)

if __name__ == "__main__":
    spade.run(main())
