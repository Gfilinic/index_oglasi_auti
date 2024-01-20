import spade
import json
from datetime import datetime
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from auxilaryFunctions import *
class DatabaseAgent(Agent):
    class CheckIfEmptyBehavior(OneShotBehaviour):
        async def on_start(self):
            print(f"Database agent is starting...")
            
        async def run(self):
            self.agent.local_data = []
            try:
                with open('Index_auti.json', 'r', encoding='utf-8') as jsonfile:
                    self.agent.local_data = json.load(jsonfile)
                    if self.agent.local_data:
                        self.agent.empty = False
            except FileNotFoundError:
                print("Local JSON file not found.")
                self.agent.empty = True


            msg = await self.receive(timeout=100000)
            if msg:
                self.agent.data = msg.body
                self.agent.sender_jid = msg.sender
                print("database agent got message")
                if self.agent.empty:
                        message = spade.message.Message(to=str(self.agent.sender_jid))
                        message.body = "File not found"
                        message.metadata["json_empty"] = True  # Add metadata indicating the JSON file is empty
                        # After updating local data
                        message.metadata["data_exists"] = False

                        print("sent message")
                        response = await send_and_wait_for_response(self,message)
                        if response:
                            data=response.body
                            try:
                                await write_json(data)
                                await self.agent.stop()
                            except json.JSONDecodeError as e:
                                print(f"Error decoding JSON: {e}")
                elif not self.agent.empty:

                    b = self.agent.ProcessDataBehavior()
                    self.agent.add_behaviour(b)
            else:
                await self.agent.stop()
                


            print("I am done, hasakey!")

    class ProcessDataBehavior(OneShotBehaviour):
        async def on_start(self):
            self.empty=self.agent.empty
        
        async def run(self):
           
                    print("Database agent: Processing data")
                    print("Last post ", str(self.agent.local_data[0]),"\n")
                    print("data:", str(self.agent.data),"\n")

                    # Check if the received data is the same as the last post in the local data
                    if self.agent.local_data[0]["poveznica"] == json.loads(self.agent.data)["poveznica"]:
                        print("Received post is the same as the last one in the database.")
                        message = spade.message.Message(to=str(self.agent.sender_jid))
                        message.body = "Data is in sync!"
                        message.metadata["json_empty"] = False
                        message.metadata["data_exists"] = True
                        await self.send(message)
                    else:
                        # Process the new post, update local data, and send a response
                        print("Received a new post. Processing...")
                        # Add your logic to process the new post here

                        # Send a response indicating successful processing
                        response_message = spade.message.Message(to=str(self.agent.sender_jid))
                        response_message.body = self.agent.local_data[0]["poveznica"]
                        response_message.metadata["json_empty"] = False
                        response_message.metadata["data_exists"] = False
                        print("sent message to top LevelAgent: ",response_message.body)
                        response = await send_and_wait_for_response(self,response_message)
                        if response:
                            data=response.body
                            try:
                                await append_json(data)
                            except json.JSONDecodeError as e:
                                print(f"Error decoding JSON: {e}")
                        await self.agent.stop()
                        # Save the updated local data to the JSON file
                        #await self.write_json(json.dumps(local_data))
    async def setup(self):
        b = self.CheckIfEmptyBehavior()
        

        self.add_behaviour(b)
        
        


