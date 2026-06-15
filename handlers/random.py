from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from util import load_prompt, send_image, send_text_buttons, chat_gpt

print("Модуль random.py успішно завантажено Python!")
router = Router()

@router.message(Command("random"))
async def random_fact(message: Message):
    prompt = load_prompt('random')
    response = await chat_gpt.send_question(prompt, 'Давай рандомний факт')
    await send_image(message, 'random')
    await send_text_buttons(message, response, {
        "random_finish": "Закінчити",
        "random_one_more": "Хочу ще факт"
    })


@router.callback_query(F.data.in_({"random_finish", "random_one_more"}))
async def random_buttons_handler(callback_query: CallbackQuery, bot: Bot):
    print(f"ХЕНДЛЕР КНОПОК RANDOM СПРАЦЮВАВ! Натиснуто: {callback_query.data}")
    await callback_query.answer()

    query = callback_query.data

    if query == "random_finish":
        from handlers.start import start
        await start(callback_query.message, bot)

    elif query == "random_one_more":
        await random_fact(callback_query.message)