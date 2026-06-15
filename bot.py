import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import credentials
from gpt import ChatGptService
from util import (load_message, send_text, send_image, show_main_menu,
                  default_callback_handler, load_prompt, send_text_buttons, DialogStates)

# Ініціалізація бота та диспетчера
bot = Bot(token=credentials.BOT_TOKEN)
dp = Dispatcher()
chat_gpt = ChatGptService(credentials.ChatGPT_TOKEN)


# Обробник команди /start
@dp.message(Command("start"))
async def start(message: Message):
    text = load_message('main')
    await send_image(message, 'main')
    await send_text(message, text)

    # Передаємо об'єкт bot та id чату, як ми налаштували в утилітах
    await show_main_menu(bot, message.chat.id, {
        'start': 'Головне меню',
        'random': 'Дізнатися випадковий цікавий факт 🧠',
        'gpt': 'Задати питання чату GPT 🤖',
        'talk': 'Поговорити з відомою особистістю 👤',
        'quiz': 'Взяти участь у квізі ❓'
    })
    prompt = load_prompt('main')
    chat_gpt.set_prompt(prompt)


# Обробник команди /random
@dp.message(Command("random"))
async def random_fact(message: Message):
    prompt = load_prompt('random')
    response = await chat_gpt.send_question(prompt, 'Давай рандомний факт')
    await send_image(message, 'random')
    await send_text_buttons(message, response, {
        "random_finish": "Закінчити",  # Змінено дефіс на підкреслення для відповідності паттерну
        "random_one_more": "Хочу ще факт"
    })
# Обробник команди /gpt
@dp.message(Command("gpt"))
async def gpt_cmd(message: Message, state: FSMContext):
    await send_image(message, 'gpt')
    await state.set_state(DialogStates.TEXT_GPT)
    await message.answer("🤖 Режим чату активовано, очікую на повідомлення")

# Обробник команди /talk
@dp.message(Command("talk"))
async def talk_cmd(message: Message, state: FSMContext):
    await send_image(message, 'talk')
    await state.set_state(DialogStates.TEXT_DIALOG)


# Обробник повідомлень, який спрацьовує лише коли користувач у стані TEXT_GPT
@dp.message(DialogStates.TEXT_GPT)
async def gpt_dialog_handler(message: Message):
    if message.text and message.text.startswith('/'):
        return
    user_text = message.text
    #await message.bot.send_chat_action(message.chat.id, action="typing")
    response = await chat_gpt.send_question(load_prompt('gpt'), user_text)
    await send_text_buttons(
        message=message,
        text=response,
        buttons={
            "gpt_finish":"Закінчити розмову ❌"
        })


# Обробник для кнопки завершення розмови з GPT
@dp.callback_query(F.data == "gpt_finish")
async def gpt_finish_callback_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await state.clear()
    await callback_query.message.answer("Розмову завершено. Повертаємось до головного меню...")
    await start(callback_query.message)

# Обробник кнопок, які починаються на "random_"
@dp.callback_query(F.data.startswith("random_"))
async def random_buttons_handler(callback_query: CallbackQuery):
    await callback_query.answer()  # Завжди гасимо "годинничок" на кнопці

    query = callback_query.data
    if query == "random_finish":
        # Перенаправляємо в start, передаючи message з callback_query
        await start(callback_query.message)
    elif query == "random_one_more":
        await random_fact(callback_query.message)



# Головна функція запуску бота
async def main():
    dp.callback_query.register(default_callback_handler)
    print("🤖 успішно запущений!")

    # Видаляємо всі повідомлення, які прилетіли боту, поки він був вимкнений
    # (щоб він не відповідав на них одночасно після увімкнення)
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot)
    finally:
        # Гарантовано закриваємо сесію клієнта при зупинці скрипта
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nБот зупинений користувачем. Бувай!")

