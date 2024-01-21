import json
import os
import spade
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, FSMBehaviour, State, Message

from telegramAgent import TelegramAgent
from negotiationAgent import BuyerAgent, SellerAgent
STATE_ONE = "CHECK_LOCAL_DATA"
STATE_TWO = "STATE_TWO"
STATE_THREE = "STATE_THREE"


class PriceFSMBehaviour(FSMBehaviour):
    async def on_start(self):
        print(f"FSM starting at initial state {self.current_state}")
        


    async def on_end(self):
        print(f"FSM finished at state {self.current_state}")
        await self.agent.stop()


class StateOne(State):
    async def run(self):
        print("I'm at state one (initial state)")
        if not os.path.exists('average_prices.json'):
            print("Prices file does not exist. Creating and populating...")
                # Load data from index_auti.json
            if self.create_local_file():
                self.agent.stop()
        else:
            self.set_next_state(STATE_TWO)
    
    def create_local_file(self):
        with open('Index_auti.json', 'r', encoding='utf-8') as index_file:
                data = json.load(index_file)

        average_prices = {}

        
        for entry in data:
            marka = entry.get('marka', 'undefined')
            cijena = entry.get('cijena', 0)

            # Exclude entries with a price of 0
            if cijena > 0:
                if marka not in average_prices:
                    average_prices[marka] = {'sum': cijena, 'count': 1}
                else:
                    average_prices[marka]['sum'] += cijena
                    average_prices[marka]['count'] += 1

        # Calculate the average for each 'Marka'
        for marka, values in average_prices.items():
            average_prices[marka]['average'] = values['sum'] / values['count']

        average_prices["Undefined"] = average_prices.pop("")
        # Save the average prices to a JSON file
        json_filename = 'average_prices.json'
        with open(json_filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(average_prices, jsonfile, indent=2, ensure_ascii=False)

        print(f"Average prices saved to {json_filename}")
        return True
    async def on_end(self):
        print("I am done")

class StateTwo(State):
    async def run(self):
        print("I'm at state two")
        # Your logic for waiting for a message with new posts goes here
        msg = await self.receive(timeout=10)
        if msg:
            data=json.loads(msg.body)
            try:
                await self.check_for_prices(data)
                await self.update_average_prices(data)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
        self.set_next_state(STATE_THREE)


    async def update_average_prices(self, new_data):
        with open('average_prices.json', 'r', encoding='utf-8') as jsonfile:
            average_prices = json.load(jsonfile)
        undefined_sum = average_prices.get("Undefined", {"sum": 0})["sum"]
        undefined_count = average_prices.get("Undefined", {"count": 0})["count"]
        for entry in new_data:
            marka = entry.get('marka', 'undefined')
            cijena = entry.get('cijena', 0)
            # Exclude entries with a price of 0
            if cijena > 0:
                if marka not in average_prices:
                    average_prices[marka] = {'sum': cijena, 'count': 1}
                else:
                    average_prices[marka]['sum'] += cijena
                    average_prices[marka]['count'] += 1
                if marka == "":
                    undefined_sum += cijena
                    undefined_count += 1
        undefined_sum += average_prices.get("Undefined", {"sum": 0})["sum"]
        undefined_count += average_prices.get("Undefined", {"count": 0})["count"]
        # Calculate the average for each 'Marka'
        for marka, values in average_prices.items():
            average_prices[marka]['average'] = values['sum'] / values['count']
        if undefined_count > 0:
            average_prices["Undefined"] = {
                'sum': undefined_sum,
                'count': undefined_count,
                'average': undefined_sum / undefined_count
            }
        else:
            # No entries with marka="", remove the "Undefined" key
            average_prices.pop("Undefined", None)
        # Remove the entry for ""
        average_prices.pop("", None)
        # Save the updated average_prices to the JSON file
        json_filename = 'average_prices.json'
        with open(json_filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(average_prices, jsonfile, indent=2, ensure_ascii=False)
        print(f"Updated average prices saved to {json_filename}")

    async def check_for_prices(self,data):
        with open('average_prices.json', 'r', encoding='utf-8') as jsonfile:
            average_prices = json.load(jsonfile)
        self.agent.notification_list = []
        counter = 0
        for entry in data:
            marka = entry.get('marka', 'Undefined')
            cijena = entry.get('cijena', 0)
            marka = "Undefined" if marka == "" else marka

            if cijena > 0:
                if marka in average_prices:
                    average_price = average_prices[marka]['average']
                    if cijena < average_price:
                                counter+=1
                                buyer_jid = f"buyer_{counter}@localhost"
                                seller_jid = f"seller_{counter}@localhost"
                                buyerAgent = BuyerAgent(buyer_jid,"buyer",cijena, seller_jid)
                                sellerAgent = SellerAgent(seller_jid,"seller",cijena, buyer_jid)
                                await buyerAgent.start()
                                await sellerAgent.start()
                               
                                received_msg = await self.receive(timeout=10)
                                if received_msg:
                                    print("Received message")
                                    negotiation_price = received_msg.body
                                    print(f"Post with marka '{marka}' has a price lower than average: {cijena} < {average_price}")
                                    notification_message = (
                                    f"Link: {entry['poveznica']}\n"
                                    f"Marka: {marka}\n"
                                    f"Cijena: {cijena}\n"
                                    f"Godina proizvodnje: {entry['godina_proizvodnje']}\n"
                                    f"-------------------------------------------------\n"
                                    f"Opis: {entry['opis']}\n"
                                    f"-------------------------------------------------\n"
                                    f"Prosječna cijena za {marka}: {int(average_price)}\n"
                                    f"Preporučena cijena za pregovaranje: {negotiation_price}\n"
                                    )
                                    self.agent.notification_list.append(notification_message)
                    else:
                        print("No offers below average!")
            

class StateThree(State):
    async def run(self):
        print("I'm at state three (final state)")
        notification_list = self.agent.notification_list
        telegram_agent = TelegramAgent("telegramAgent@localhost", "telegram")
        await telegram_agent.start()
        message = spade.message.Message(to=str(telegram_agent.jid))
        message.body = json.dumps(notification_list)
        await self.send(message)
        await wait_until_finished(telegram_agent)
        self.kill()

class PriceAgent(Agent):
    async def setup(self):
        fsm = PriceFSMBehaviour()
        fsm.add_state(name=STATE_ONE, state=StateOne(), initial=True)
        fsm.add_state(name=STATE_TWO, state=StateTwo())
        fsm.add_state(name=STATE_THREE, state=StateThree())
        fsm.add_transition(source=STATE_ONE, dest=STATE_TWO)
        fsm.add_transition(source=STATE_TWO, dest=STATE_THREE)
        fsm.add_transition(source=STATE_THREE, dest=STATE_TWO)
        self.add_behaviour(fsm)



"""
async def main():
    price_agent = PriceAgent("price@localhost", "price")
    await price_agent.start()
    print("Price agent started. Check its console to see the output.")
    await wait_until_finished(price_agent)
    await price_agent.stop()

if __name__ == "__main__":
    spade.run(main())
"""

