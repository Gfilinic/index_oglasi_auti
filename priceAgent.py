import json
import os
import spade
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, FSMBehaviour, State, Message

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
        self.set_next_state(STATE_TWO)


class StateTwo(State):
    async def run(self):
        print("I'm at state two")

        # Your logic for waiting for a message with new posts goes here
        msg = await self.receive(timeout=1)
        if msg:
            # Transition to the next state
            self.set_next_state(STATE_THREE)


class StateThree(State):
    async def run(self):
        print("I'm at state three (final state)")

        # Your logic for calculating average prices and saving to prices.json goes here

        # No final state is set since this is a final state


class PriceAgent(Agent):
    async def setup(self):
        fsm = PriceFSMBehaviour()
        fsm.add_state(name=STATE_ONE, state=StateOne(), initial=True)
        fsm.add_state(name=STATE_TWO, state=StateTwo())
        fsm.add_state(name=STATE_THREE, state=StateThree())
        fsm.add_transition(source=STATE_ONE, dest=STATE_TWO)
        fsm.add_transition(source=STATE_TWO, dest=STATE_THREE)
        self.add_behaviour(fsm)



async def main():
    price_agent = PriceAgent("price@localhost", "price")
    await price_agent.start()
    print("Price agent started. Check its console to see the output.")
    await wait_until_finished(price_agent)
    await price_agent.stop()

if __name__ == "__main__":
    spade.run(main())