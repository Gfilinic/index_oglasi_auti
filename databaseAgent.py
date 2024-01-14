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
            local_data = []
            try:
                with open('Index_auti.json', 'r', encoding='utf-8') as jsonfile:
                    local_data = json.load(jsonfile)
            except FileNotFoundError:
                print("Local JSON file not found.")
                empty = True


            msg = await self.receive(timeout=100000)
            if msg:
                data = msg.body
                sender_jid = msg.sender
                print("database agent got message")
                if empty:
                        print("empty database")
                        
                        message = spade.message.Message(to=str(sender_jid))
                        message.body = "File not found"
                        message.metadata["json_empty"] = True  # Add metadata indicating the JSON file is empty
                        # After updating local data
                        message.metadata["data_exists"] = False

                        print("sent message")
                        response = await self.send_and_wait_for_response(message)
                        if response:
                            data=response.body
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

        async def send_and_wait_for_response(self, message):
            response = None
            try:
                await self.send(message)
                response = await self.receive(timeout=100000)
                if response: 
                    return response
            except Exception:
                print("No response")
            
            return response

    async def setup(self):
        b = self.DatabaseAgentBehavior()
        self.add_behaviour(b)


