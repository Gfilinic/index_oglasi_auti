import time
import asyncio
import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
import random
from spade.message import Message

class BuyerAgent(Agent):
    class BuyerBehaviour(CyclicBehaviour):
        async def on_start(self):
            await asyncio.sleep(0.5)
            print(f"{self.agent.jid} agent started!\n")
            self.max_price = self.agent.price
            self.min_price = int(8/10 * self.max_price)
            self.proposal = random.uniform(self.min_price, self.max_price)
            self.round = 1
            self.accepted_offer = False
            self.minimal_acceptance_price = self.min_price + (self.max_price - self.min_price) * 0.1
            self.acceptance_threshold = self.minimal_acceptance_price
            self.concession_factor = 0.1  # Concession factor for adjusting offers
            self.feedback = []

        async def run(self):
            # Wait for the seller agent to start
            if not self.accepted_offer:
                msg = Message(to=self.agent.seller_jid)
                msg.body = str(self.proposal)
                await self.send(msg)

                received_msg = await self.receive(timeout=20)

                if received_msg:
                    received_proposal = float(received_msg.body)
                    print(f"{self.agent.jid} (Round {self.round}): {self.proposal}")

                    # Check if the received offer is below the minimal acceptance price
                    if received_proposal <= self.minimal_acceptance_price:
                        print(f"{self.agent.jid} (Round {self.round}): Accepted the offer! (Minimal acceptance price reached)")
                        self.accepted_offer = True
                        self.accepted_proposal = received_proposal
                        msg = Message(to="price@localhost")
                        msg.body = str(int(self.accepted_proposal))
                        await self.send(msg)
                        
                        await self.agent.stop()
                    else:
                        # Adjust acceptance threshold based on negotiation progress
                        acceptance_threshold_decay = 0.95
                        self.acceptance_threshold *= acceptance_threshold_decay

                        # Apply concession strategy
                        self.proposal = max(received_proposal, self.min_price)
                        self.proposal *= (1 + self.concession_factor)
                        self.proposal = min(self.proposal, self.max_price)

                        print(f"{self.agent.jid} (Round {self.round}): Counteroffering with {self.proposal}\n")
                        msg = Message(to=self.agent.seller_jid)
                        msg.body = str(self.proposal)
                        await self.send(msg)
                        self.feedback.append((self.round, received_proposal, self.proposal))
                        self.round += 1
                else:
                    print(f"{self.agent.jid} (Round {self.round}): Didn't receive anything")

                    

        async def on_end(self):
            pass
            

    def __init__(self, jid, password, price, seller_jid):
        super().__init__(jid, password)
        self.price = price
        self.seller_jid = seller_jid

    async def setup(self):
        b = self.BuyerBehaviour()
        self.add_behaviour(b)

class SellerAgent(Agent):
    class SellerBehaviour(CyclicBehaviour):
        async def on_start(self):
            print(f"{self.agent.jid} agent started!\n")
            self.max_price = self.agent.price
            self.min_price = float(6/10 * self.max_price)
            self.proposal = random.uniform(self.min_price, self.max_price)
            self.round = 1

        async def run(self):
            # Wait for the buyer agent to start

            received_msg = await self.receive(timeout=20)

            if received_msg:
                print(f"{self.agent.jid} (Round {self.round}): My proposal {self.proposal}!")

                # Apply concession strategy
                self.proposal *= 0.9
                self.proposal = max(self.min_price, self.proposal)

                print(f"{self.agent.jid} (Round {self.round}): Counteroffering with {self.proposal}\n")
                msg = Message(to=self.agent.buyer_jid)
                msg.body = str(self.proposal)
                await self.send(msg)
            else:
                await self.agent.stop()
            self.round += 1

        async def on_end(self):
            pass

    def __init__(self, jid, password, price, buyer_jid):
        super().__init__(jid, password)
        self.price = price
        self.buyer_jid = buyer_jid

    async def setup(self):
        b = self.SellerBehaviour()
        self.add_behaviour(b)
'''
async def main():
    price = 3000
    buyer = BuyerAgent("buyer@localhost", "123456789", price)
    seller = SellerAgent("seller@localhost", "123456789", price)

    await buyer.start()
    await seller.start()

if __name__ == "__main__":
    spade.run(main())

'''

