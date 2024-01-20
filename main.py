import asyncio
import spade
import json
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from auxilaryFunctions import *
from scraping import IndexScraper
from databaseAgent import DatabaseAgent
from priceAgent import PriceAgent

class TopLevelAgent(Agent):
    class PeriodicTaskBehaviour(CyclicBehaviour):
        async def on_start(self):
            self.scraper_initialized = False
            self.price_agent = PriceAgent("price@localhost", "price")
        

        async def run(self):
            print("---------------------")
            await self.initialize_scraper()

            data = self.scraper.sort_data()
            comparison_task = asyncio.create_task(self.start_agents(data))
            await asyncio.gather(comparison_task)
            await asyncio.sleep(600)

        async def start_agents(self, data):
            database_agent = DatabaseAgent("database@localhost", "db")
            await database_agent.start()
            last_post = data[0] if data else None
            message = spade.message.Message(to=str(database_agent.jid))
            message.body = json.dumps(last_post)
            response = await send_and_wait_for_response(self,message)

            # Process the response based on its metadata
            if response:
                print("got response!", response)
                if response.metadata.get("data_exists", True):
                    print("No new posts.")
                elif response.metadata.get("json_empty", True):
                    print("No local file.")
                    message = spade.message.Message(to=str(database_agent.jid))
                    message.body = json.dumps(data)
                    await self.send(message)
                else:
                    print("New posts detected")
                    last_post = response.body
                    last_post_index = next((i for i, post in enumerate(data) if post["poveznica"] == last_post), None)
                    posts_to_send = data[:last_post_index] if last_post_index is not None else data
                    if posts_to_send:
                        message = spade.message.Message(to=str(database_agent.jid))
                        message.body = json.dumps(posts_to_send)
                        await self.send(message)
                        print(f"Sent {len(posts_to_send)} posts to DatabaseAgent.")
                        
                        await self.price_agent.start()
                        
                        message = spade.message.Message(to=str(self.price_agent.jid))
                        message.body = json.dumps(posts_to_send)
                        await self.send(message)
                        print(f"Sent {len(posts_to_send)} posts to PriceAgent.")


        
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
    try:
        await wait_until_finished(top_agent)
    except KeyboardInterrupt:
        top_agent.stop()
        print("Interrupted!")

if __name__ == "__main__":
    spade.run(main())
