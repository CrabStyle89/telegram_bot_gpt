from aiogram.fsm.state import State, StatesGroup
from aiogram import Bot
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
    FSInputFile,
    BotCommandScopeChat
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
import os
import credentials
from gpt import ChatGptService


# Примітка: для роботи методів, які використовують self.bot або викликаються поза хендлерами,
# aiogram зазвичай передає об'єкт bot автоматично в хендлер, якщо додати його в аргументи.


# конвертує об'єкт user в рядок
def dialog_user_info_to_str(user_data: dict) -> str:
    mapper = {
        'language_from': 'Мова оригіналу',
        'language_to': 'Мова перекладу',
        'text_to_translate': 'Текст для перекладу'
    }
    # Виправлено помилку в map (у python map приймає функцію та ітеровані об'єкти,
    # для словників простіше використати генератор списків)
    return '\n'.join(f"{mapper[k]}: {v}" for k, v in user_data.items() if k in mapper)


# надсилає в чат текстове повідомлення (Markdown)
async def send_text(message: Message, text: str) -> Message:
    if text.count('_') % 2 != 0:
        warning = f"Рядок '{text}' є невалідним з точки зору markdown. Скористайтеся методом send_html()"
        print(warning)
        return await message.answer(warning)

    return await message.answer(text, parse_mode=ParseMode.MARKDOWN)


# надсилає в чат html повідомлення
async def send_html(message: Message, text: str) -> Message:
    return await message.answer(text, parse_mode=ParseMode.HTML)


# надсилає в чат текстове повідомлення, та додає до нього кнопки
async def send_text_buttons(message: Message, text: str, buttons: dict) -> Message:
    # Використовуємо зручний InlineKeyboardBuilder з aiogram 3
    builder = InlineKeyboardBuilder()
    for key, value in buttons.items():
        builder.row(InlineKeyboardButton(text=str(value), callback_data=str(key)))

    return await message.answer(
        text=text,
        reply_markup=builder.as_markup(),
        thread_id=message.message_thread_id
    )


# надсилає в чат фото
async def send_image(message: Message, name: str) -> Message:
    path = f'resources/images/{name}.jpg'

    if not os.path.exists(path):
        warning_msg = f"Зображення {name} не знайдено за шляхом {path}."
        print(warning_msg)
        return await message.answer(warning_msg)

    # Вместо open() оборачиваем путь к файлу в FSInputFile
    photo_file = FSInputFile(path)

    return await message.answer_photo(photo=photo_file)


# відображає команду та головне меню
# Оскільки set_my_commands викликається у бота, нам потрібен об'єкт bot
async def show_main_menu(bot: Bot, chat_id: int, commands: dict):
    command_list = [BotCommand(command=key, description=value) for key, value in commands.items()]

    await bot.set_my_commands(
        commands=command_list,
        scope=BotCommandScopeChat(chat_id=chat_id)
    )
    # В aiogram 3 кнопка "Меню" біля поля вводу керується автоматично
    # на основі наявності команд для цього scope, тому set_chat_menu_button зазвичай не потрібен.


# видаляємо команди для конкретного чату
async def hide_main_menu(bot: Bot, chat_id: int):
    await bot.delete_my_commands(
        scope=BotCommandScopeChat(chat_id=chat_id)
    )
# завантажує повідомлення з папки /resources/messages/
def load_message(name):
    with open("resources/messages/" + name + ".txt", "r",
              encoding="utf8") as file:
        return file.read()


# завантажує промпт з папки /resources/messages/
def load_prompt(name):
    with open("resources/prompts/" + name + ".txt", "r",
              encoding="utf8") as file:
        return file.read()


# Хендлер для обробки натискань на кнопки
async def default_callback_handler(callback_query: CallbackQuery):
    # Обов'язково відповідаємо на колбек, щоб кнопка не "зависала"
    await callback_query.answer()

    query = callback_query.data
    # Відправляємо повідомлення в той самий чат, де натиснули кнопку
    await send_html(callback_query.message, f'You have pressed button with <b>{query}</b> callback')



class DialogStates(StatesGroup):
    TEXT_GPT = State()
    TEXT_DIALOG = State()
    TEXT_QUIZ = State()
    TEXT_TRANSLATE = State()

chat_gpt = ChatGptService(credentials.ChatGPT_TOKEN)