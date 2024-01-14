import spade
import json
from datetime import datetime
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
                    if local_data:
                        empty = False
            except FileNotFoundError:
                print("Local JSON file not found.")
                empty = True


            msg = await self.receive(timeout=100000)
            if msg:
                data = msg.body
                sender_jid = msg.sender
                print("database agent got message")
                if empty:
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
                elif not empty:
                    print("Last post ", str(local_data[0]),"\n")
                    print("data:", str(data),"\n")

                    # Check if the received data is the same as the last post in the local data
                    if local_data[0]["poveznica"] == json.loads(data)["poveznica"]:
                        print("Received post is the same as the last one in the database.")
                        message = spade.message.Message(to=str(sender_jid))
                        message.body = "File not found"
                        message.metadata["json_empty"] = False
                        message.metadata["data_exists"] = True
                        await self.send(message)
                    else:
                        # Process the new post, update local data, and send a response
                        print("Received a new post. Processing...")
                        # Add your logic to process the new post here

                        # Send a response indicating successful processing
                        response_message = spade.message.Message(to=str(sender_jid))
                        response_message.body = local_data[0]["poveznica"]
                        response_message.metadata["json_empty"] = False
                        response_message.metadata["data_exists"] = False
                        print("sent message to top LevelAgent: ",response_message.body)
                        response = await self.send_and_wait_for_response(response_message)
                        if response:
                            data=response.body
                            try:
                                await self.append_json(data)
                            except json.JSONDecodeError as e:
                                print(f"Error decoding JSON: {e}")
                        
                        # Save the updated local data to the JSON file
                        #await self.write_json(json.dumps(local_data))


            print("I am done, hasakey!")
            self.kill()
        
        async def write_json(self,data):
            json_filename = 'Index_auti.json'
            with open(json_filename, 'w', encoding='utf-8') as jsonfile:
            # Use the json.dump method to write data to the JSON file
                 json.dump(json.loads(data), jsonfile, indent=2, ensure_ascii=False)
        
        async def append_json(self,data):
            json_filename = 'Index_auti.json'
            try:
                with open(json_filename, 'r', encoding='utf-8') as existing_file:
                    existing_data = json.load(existing_file)
            except FileNotFoundError:
                existing_data = []
            combined_data = existing_data + json.loads(data)
            combined_data = sorted(combined_data, key=lambda x: datetime.strptime(x['datum_objave'], "%d.%m.%Y %H:%M"), reverse=True)
            # Write the combined data to the file
            with open(json_filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(combined_data, jsonfile, indent=2, ensure_ascii=False)

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


