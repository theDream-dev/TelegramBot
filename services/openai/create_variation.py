import io

import openai

import config as cfg
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.types import ChatActions
from PIL import Image

from buttons.buttons import create_exit_button
from states import VariateImage

# Set up OpenAI API key
openai.api_key = cfg.AI_TOKEN

# Set up Telegram bot
bot = Bot(cfg.TG_TOKEN)

"""Image variation part"""


async def variation_image_welcome(message: types.Message):

    # creating button
    keyboard = create_exit_button()

    await bot.send_message(message.chat.id,
                           "Это режим генерации вариаций картинок\. Тебе необходимо загрузить КВАДРТАТНУЮ картинку размером не более 4 мб и я сделаю её вариации\!",
                           parse_mode="MarkdownV2")
    await bot.send_message(message.chat.id, "Жду твой запрос\.", parse_mode="MarkdownV2")
    await bot.send_message(message.chat.id, "Чтобы выйти из режима нажмите кнопку", parse_mode="MarkdownV2",
                           reply_markup=keyboard)

    # now waiting for prompt
    await VariateImage.wait_prompt.set()


async def variate_image(message: types.Message, state: FSMContext):
    """ Create an image variation"""

    # Get the prompt from the user

    try:
        prompt = message.text

        if prompt == "Выйти из режима":
            await bot.send_message(message.chat.id, "Произошла деактивация режима генерации вариаций картинки...")
            await bot.send_message(message.chat.id, "Бот не будет реагировать на запросы до следующего выбора режима")
            await state.finish()

        elif prompt.startswith('/'):
            await bot.send_message(message.chat.id, "Вероятно, Вы не нажали кнопку <выйти из режима>!")

        else:
            await bot.send_message(message.chat.id, "Кажется, Вы не прислали фото!")

    except:
        flag_size = True
        flag_square = True

        photo = message.photo[-1]  # Выбираем самое большое фото из нескольких

        print('photo done')

        # Получаем информацию о фото

        file_id = photo.file_id
        file_info = await bot.get_file(file_id)
        file_size = file_info.file_size  # Размер фото в байтах
        print('info done')

        # Проверяем, что размер фото не превышает 4 МБ
        if file_size > 4 * 1024 * 1024:
            await bot.send_message(message.chat.id, text="Фото должно быть не более 4 МБ!")
            print('size done')
            flag_size = False

        # Загружаем фото в память
        file_bytes = await bot.download_file(file_info.file_path)
        image = Image.open(io.BytesIO(file_bytes.read()))

        # Конвертируем изображение в цветовое пространство RGB
        image = image.convert('RGB')
        print('load done')

        # Проверяем формат фото
        if image.format != 'PNG':
            # Если формат не PNG, конвертируем в PNG
            buffer = io.BytesIO()
            image.save(buffer, 'PNG')

            my_photo = buffer.getvalue()

            buffer.seek(0)

            await bot.send_photo(message.chat.id, photo=buffer,
                                 caption="Фото было конвертировано в формат PNG.")
        else:
            # Фото уже в формате PNG, можем его использовать
            # Ваш код обработки фото здесь
            await bot.send_message(message.chat.id, text="Фото в формате PNG.")

        # Проверяем, что фото квадратное
        if photo.width != photo.height:
            await bot.send_message(message.chat.id, text="Фото должно быть квадратным!")
            flag_square = False

        # Фото прошло проверку, можем его использовать

        if (flag_size is True) and (flag_square is True):
            print('good')

            # pretend that the bot generates an image
            await bot.send_chat_action(message.chat.id, ChatActions.UPLOAD_PHOTO)

            # # call the OpenAI API
            variation_response = openai.Image.create_variation(
                image=my_photo,
                n=3,
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
            generated_image_url = variation_response["data"] # extract image URL from response
            # generated_image = requests.get(generated_image_url).content  # download the image
            # with open(generated_image_filepath, "wb") as image_file:
            #     image_file.write(generated_image)  # write the image to the file

            for im in generated_image_url:

                await bot.send_photo(message.chat.id, im["url"])

            # await state.finish()

            # return generated_image_filepath

        else:
            print('another')


def register_variate_image(dp: Dispatcher):
    dp.register_message_handler(variation_image_welcome, commands=["create_variation"])
    dp.register_message_handler(variate_image, state=VariateImage.wait_prompt, content_types=[types.ContentType.PHOTO,
                                                                                              types.ContentType.TEXT])
