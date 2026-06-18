from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from util import send_image, load_prompt, send_text_buttons, DialogStates, chat_gpt, send_text
from handlers.start import start

router = Router()

# Обробник команди /talk
@router.message(Command("talk"))
async def talk_cmd(message: Message, state: FSMContext):
    await state.clear()  # Скидаємо минулі розмови
    await send_image(message, 'talk')  # Надсилаємо картинку для режиму talk

    # Пропонуємо вибір зірок.
    # Ключ (callback_data) починається з "talk_", щоб ми легко його відфільтрували
    await send_text_buttons(
        message=message,
        text="З ким ти хочеш поговорити?",
        buttons={
            "talk_cobain": "Курт Кобейн",
            "talk_hawking": "Стівен Хокінг",
            "talk_nietzsche": "Фрідріх Ніцсше",
            "talk_queen": "Квін",
            "talk_tolkien": "Дж. Р. Р. Толкін"
        }
    )
# Обробник натискання на кнопки вибору особистості
@router.callback_query(F.data.startswith("talk_") & (F.data != "talk_finish"))
async def talk_select_hero_hendler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    hero = callback_query.data.replace("talk_", "")
    prompt = load_prompt(f"talk_{hero}")
    chat_gpt.set_prompt(prompt)
    await state.set_state(DialogStates.TEXT_DIALOG)
    first_greet = await chat_gpt.add_message("Привітайся зі мною у своєму унікальному стилі, але дуже коротко.")

    # Надсилаємо репліку зірки користувачу разом з кнопкою закінчити
    await send_text_buttons(
        message=callback_query.message,
        text=first_greet,
        buttons={"talk_finish": "Закінчити розмову ❌"}
    )

# Обробник повідомлень
@router.message(DialogStates.TEXT_DIALOG)
async def talk_dialog_handler(message: Message):
    # Якщо користувач ввів іншу команду — ігноруємо
    if message.text and message.text.startswith('/'):
        return

    user_text = message.text

    # Відправляємо репліку користувача у вже налаштований діалог через add_message
    response = await chat_gpt.add_message(user_text)

    # Повертаємо відповідь Кобейна чи Хокінга з кнопкою завершення
    await send_text_buttons(
        message=message,
        text=response,
        buttons={"talk_finish": "Закінчити розмову ❌"}
    )
# Обробник кнопки "Закінчити" для режиму відомих людей
@router.callback_query(F.data == "talk_finish")
async def talk_finish_callback_handler(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.answer()
    await state.clear()
    await callback_query.message.answer("Духовний сеанс завершено. Повертаємось...")
    await start(callback_query.message, bot)