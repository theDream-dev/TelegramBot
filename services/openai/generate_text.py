import openai

import config as cfg
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.types import ChatActions, CallbackQuery, ReplyKeyboardMarkup

# from buttons.buttons import keyboard
from buttons.buttons import create_exit_button
from states import GenerateText

# Set up OpenAI API key
openai.api_key = cfg.AI_TOKEN

# Set up Telegram bot
bot = Bot(cfg.TG_TOKEN)
dp = Dispatcher(bot)


"""Classic OpenAI part"""


messages_arr = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "hello i am a new gpt user"},
    {"role": "assistant", "content": "Greetings! How can i help you?"},
]


def update(messages, role, content):

    # check message_arr length
    if len(messages_arr) > 20:
        del messages_arr[3:]

    messages_arr.append({"role": role, "content": content})
    return messages_arr


# @dp.message_handler(commands=['generate_text'])
async def generation_text_welcome(message: types.Message):

    # creating button
    keyboard = create_exit_button()

    await bot.send_message(message.chat.id,
                           "Так \- так\. Ты перешел в режим классического помощника\. Можешь задать мне любой вопрос\!",
                           parse_mode="MarkdownV2")
    await bot.send_message(message.chat.id, "Как я могу вам помочь\?", parse_mode="MarkdownV2")
    await bot.send_message(message.chat.id, "Чтобы выйти из режима, нажмите кнопку", parse_mode="MarkdownV2",
                           reply_markup=keyboard)

    # now waiting for prompt
    await GenerateText.wait_prompt.set()


async def respond_to_question(message: types.Message, state: FSMContext):

    update(messages_arr, "user", message.text)

    # pretend that the bot generates a response
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)

    # Get the question from the user
    question = message.text

    if question == "Выйти из режима":
        await bot.send_message(message.chat.id, "Произошла деактивация режима классического помощника...")
        await bot.send_message(message.chat.id, "Бот не будет реагировать на запросы до следующего выбора режима")
        await state.finish()

    elif question.startswith('/'):
        await bot.send_message(message.chat.id, "Вероятно, Вы не нажали кнопку <выйти из режима>!")

    else:

        # Call OpenAI's GPT-3 API to generate a response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages_arr
        )

        # Get the best answer from the API response
        answer = response['choices'][0]['message']['content']

        # If the answer contains code, output it as a code block
        if "```" in answer:
            code = answer.replace("```", "")
            await bot.send_message(message.chat.id, text=f"```\n{code}\n```", parse_mode="MarkdownV2")

        else:
            await bot.send_message(message.chat.id, text=answer)

        await bot.send_message(message.chat.id, str(len(messages_arr)))

        # update contex array
        update(messages_arr, "assistant", answer)


def register_generate_text(dp: Dispatcher):
    dp.register_message_handler(generation_text_welcome, commands=["generate_text"])
    dp.register_message_handler(respond_to_question, state=GenerateText.wait_prompt)
