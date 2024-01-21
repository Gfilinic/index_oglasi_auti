import spade
import json
from datetime import datetime
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from auxilaryFunctions import *
from telegram import Bot
class TelegramAgent(Agent):
    class TelegramAgentBehavior(OneShotBehaviour):
        async def on_start(self):
            print(f"Telegram agent is starting...")
            self.bot_token = '6813545506:AAHPft3GZR6cU37ak2cQu4ueA0g2fnVcBPk'
            self.chat_id = '1048753987' 

            #message = "Hello, this is a notification from the Spade agent!"
            #await self.send_telegram_notification(bot_token, chat_id, message)

        async def send_telegram_notification(self, bot_token, chat_id, message):
            bot = Bot(token=bot_token)
            await bot.send_message(chat_id=chat_id, text=message)
            print("Notification sent to Telegram!")
        async def run(self):
            print("run the bot")
            msg = await self.receive(timeout=30)
            if msg:
                notification_list = json.loads(msg.body)
                for entry in notification_list:
                    message = f"Pozdrav, ovaj oglas mogao bi te zanimati\n{entry}"
                    await self.send_telegram_notification(self.bot_token, self.chat_id, message)
            else:
                print("Nemam obavijesti za poslati")

            '''
            msg = await self.receive(timeout=100000)
            if msg:
                data = msg.body
                sender_jid = msg.sender
                print("database agent got message")
            '''
            
               

    async def setup(self):
        b = self.TelegramAgentBehavior()
        self.add_behaviour(b)

async def main():
    telegram_agent = TelegramAgent("telegramAgent@localhost", "telegram")
    await telegram_agent.start()

    print("Wait until user interrupts with ctrl+C")
    await wait_until_finished(telegram_agent)

if __name__ == "__main__":
    spade.run(main())

