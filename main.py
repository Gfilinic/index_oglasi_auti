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
            #message = spade.message.Message(to=str(database_agent.jid))
            #message.body = json.dumps(data)
            #await self.send(message)
            last_post = data[0] if data else None
            message = spade.message.Message(to=str(database_agent.jid))
            message.body = json.dumps(last_post)
            response = await self.send_and_wait_for_response(message)

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


        async def send_and_wait_for_response(self, message):
            response = None
            try:
                await self.send(message)
                response = await self.receive(timeout=100000)
                if response: 
                    return response
            except Exception:
                print("No response")

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
