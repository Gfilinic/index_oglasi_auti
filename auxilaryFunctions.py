from datetime import datetime
import json
async def write_json(data):
            json_filename = 'Index_auti.json'
            with open(json_filename, 'w', encoding='utf-8') as jsonfile:
            # Use the json.dump method to write data to the JSON file
                 json.dump(json.loads(data), jsonfile, indent=2, ensure_ascii=False)
        
async def append_json(data):
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