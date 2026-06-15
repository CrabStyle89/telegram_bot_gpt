from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from util import load_message, send_image, send_text, show_main_menu, load_prompt, chat_gpt


router = Router()


@router.message(Command("start"))
async def start(message: Message, bot: Bot):
    text = load_message('main')
    await send_image(message, 'main')
    await send_text(message, text)

    await show_main_menu(bot, message.chat.id, {
        'start': 'Головне меню',
        'random': 'Дізнатися випадковий цікавий факт 🧠',
        'gpt': 'Задати питання чату GPT 🤖',
        'talk': 'Поговорити з відомою особистістю 👤',
        'quiz': 'Взяти участь у квізі ❓'
    })
    prompt = load_prompt('main')
    chat_gpt.set_prompt(prompt)