from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from util import send_image, load_prompt, send_text_buttons, DialogStates, chat_gpt
from handlers.start import start

router = Router()

async def show_language_selection(message: Message):
    await send_text_buttons(
        message=message,
        text="Обери мову, на яку потрібно перекласти твій текст:",
        buttons={
            "lang_en": "Англійська",
            "lang_de": "Німецька",
            "lang_es": "Іспанська",
            "lang_pl": "Польська"
        }
    )

# Обробник команди /translate
@router.message(Command("translate"))
async def translate_cmd(message: Message, state: FSMContext):
    await state.clear()
    await send_image(message, 'translate')
    await show_language_selection(message)

# Обробник вибору мови
@router.callback_query(F.data.startswith("lang_"))
async def translate_select_lang_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    languages = {
        "lang_en": "Англійську 🇬🇧",
        "lang_de": "Німецьку 🇩🇪",
        "lang_es": "Іспанську 🇪🇸",
        "lang_pl": "Польську 🇵🇱"
    }
    chosen_lang_raw = callback_query.data
    chosen_lang_text = languages.get(chosen_lang_raw, "обрану мову")
    await state.update_data(target_lang=chosen_lang_text)
    await state.set_state(DialogStates.TEXT_TRANSLATE)
    await callback_query.message.answer(f"режим перекладача активовано. Відсилай мені будь-який текст, і я перекладу його на *{chosen_lang_text}*.")

# Обробник тексту, який треба перекласти
@router.message(DialogStates.TEXT_TRANSLATE)
async def translate_text_handler(message: Message, state: FSMContext):
    if message.text and message.text.startswith('/'):
        return

    user_text = message.text
    user_data = await state.get_data()
    target_lang = user_data.get("target_lang","Англійську")
    prompt = load_prompt("translate")
    gpt_task = f"Переклади цей текст на {target_lang}:\n\n{user_text}"
    await message.answer("**Перекладаю...**")
    translation = await chat_gpt.send_question(prompt, gpt_task)

    await send_text_buttons(
        message=message,
        text=translation,
        buttons={
            "translate_change_lang": "Змінити мову",
            "translate_finish": "Закінчити ❌"
        }
    )

# Обробник кнопки "Змінити мову"
@router.callback_query(F.data == "translate_change_lang")
async def translate_change_lang_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await show_language_selection(callback_query.message)

    # Обробник кнопки "Закінчити"
@router.callback_query(F.data == "translate_finish")
async def translate_finish_handler(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.answer()
    await state.clear()
    await callback_query.message.answer("Режим перекладача вимкнено.")
    await start(callback_query.message, bot)