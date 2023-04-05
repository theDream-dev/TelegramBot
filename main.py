import asyncio

import openai
import aiogram
import config as cfg
from aiogram import Bot, types, Dispatcher
from aiogram.utils import executor
from aiogram.types import ParseMode, ChatActions, Message
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from services.openai.start import register_start
from services.openai.generate_text import register_generate_text
from services.openai.generate_image import register_generate_image
from services.openai.create_variation import register_variate_image

from commands import set_default_commands

# Set up OpenAI API key
openai.api_key = cfg.AI_TOKEN

storage = MemoryStorage()


def register_all_handlers(dp):
    register_start(dp)
    register_generate_text(dp)
    register_generate_image(dp)
    register_variate_image(dp)


async def main():

    # Set up Telegram bot
    bot = Bot(cfg.TG_TOKEN)
    dp = Dispatcher(bot, storage=storage)

    register_all_handlers(dp)

    # start
    try:
        await set_default_commands(dp)
        await dp.start_polling()

    except:
        print('smth got wrong')


if __name__ == '__main__':
    try:
        asyncio.run(main())

    except (KeyboardInterrupt, SystemExit):
        print(f"Bot stopped! Error: {KeyboardInterrupt} {SystemExit}")
        print("[INFO] Bot stopped")
