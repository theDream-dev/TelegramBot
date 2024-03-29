from aiogram.dispatcher import Dispatcher
from aiogram import types


async def set_default_commands(dp: Dispatcher):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Start bot"),
        #types.BotCommand("generate_image", "Generate image"),
        types.BotCommand("generate_text", "classic openAI helper"),
        # types.BotCommand("help", "Get help"),
        # types.BotCommand("feedback", "Write feedback")
    ])
