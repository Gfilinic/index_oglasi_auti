import spade
import json
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour

class DatabaseAgent(Agent):
    class DatabaseAgentBehavior(OneShotBehaviour):
        async def on_start(self):
            print(f"Database agent is starting...")
            
        async def run(self):
            msg = await self.receive(timeout=100000)
            if msg:
                data = msg.body

                try:
                    await self.write_json(data)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
            print("I am done, hasakey!")
            self.kill()
        
        async def write_json(self,data):
            json_filename = 'Index_auti.json'
            with open(json_filename, 'w', encoding='utf-8') as jsonfile:
            # Use the json.dump method to write data to the JSON file
                 json.dump(json.loads(data), jsonfile, indent=2, ensure_ascii=False)


    async def setup(self):
        b = self.DatabaseAgentBehavior()
        self.add_behaviour(b)


