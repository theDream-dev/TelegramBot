import openai

import config as cfg
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.types import ChatActions

from buttons.buttons import create_exit_button
from states import GenerateImage

# Set up OpenAI API key
openai.api_key = cfg.AI_TOKEN

# Set up Telegram bot
bot = Bot(cfg.TG_TOKEN)

"""Image generation part"""


async def generation_image_welcome(message: types.Message):

    # creating button
    keyboard = create_exit_button()

    await bot.send_message(message.chat.id,
                           "Это режим генерации картинок\. Давай проверим, насколько хороша твоя фантазия\!",
                           parse_mode="MarkdownV2")
    await bot.send_message(message.chat.id, "Жду твой запрос\.", parse_mode="MarkdownV2")
    await bot.send_message(message.chat.id, "Чтобы выйти из режима нажмите кнопку", parse_mode="MarkdownV2",
                           reply_markup=keyboard)

    # now waiting for prompt
    await GenerateImage.wait_prompt.set()


async def generate_image(message: types.Message, state: FSMContext):
    """ Create an image """

    # Get the prompt from the user
    prompt = message.text

    if prompt == "Выйти из режима":
        await bot.send_message(message.chat.id, "Произошла деактивация режима генерации картинок...")
        await bot.send_message(message.chat.id, "Бот не будет реагировать на запросы до следующего выбора режима")
        await state.finish()

    elif prompt.startswith('/'):
        await bot.send_message(message.chat.id, "Вероятно, Вы не нажали кнопку <выйти из режима>!")

    else:

        # pretend that the bot generates an image
        await bot.send_chat_action(message.chat.id, ChatActions.UPLOAD_PHOTO)

        # call the OpenAI API
        generation_response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512",
            response_format="url",
        )

        # print response
        # print(generation_response)

        # save the image

        # i = 0
        # flnm = "images\\image" + str(i) + ".png"
        #
        # while path.exists(flnm):
        #     flnm = "images\\image" + str(i) + ".png"
        #     i += 1
        #
        # generated_image_filepath = os.path.join(flnm)
        generated_image_url = generation_response["data"][0]["url"]  # extract image URL from response
        # generated_image = requests.get(generated_image_url).content  # download the image
        # with open(generated_image_filepath, "wb") as image_file:
        #     image_file.write(generated_image)  # write the image to the file

        await bot.send_photo(message.chat.id, generated_image_url)

        # await state.finish()

        # return generated_image_filepath


def register_generate_image(dp: Dispatcher):
    dp.register_message_handler(generation_image_welcome, commands=["generate_image"])
    dp.register_message_handler(generate_image, state=GenerateImage.wait_prompt)
