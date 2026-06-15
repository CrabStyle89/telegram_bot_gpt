from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from util import send_image, load_prompt, send_text_buttons, DialogStates, chat_gpt
from handlers.start import start


router = Router()


@router.message(Command("gpt"))
async def gpt_cmd(message: Message, state: FSMContext):
    await send_image(message, 'gpt')
    await state.set_state(DialogStates.TEXT_GPT)
    await message.answer("🤖 Режим чату активовано, очікую на повідомлення")


@router.message(DialogStates.TEXT_GPT)
async def gpt_dialog_handler(message: Message):
    if message.text and message.text.startswith('/'):
        return

    user_text = message.text
    response = await chat_gpt.send_question(load_prompt('gpt'), user_text)
    await send_text_buttons(
        message=message,
        text=response,
        buttons={"gpt_finish": "Закінчити розмову ❌"}
    )


@router.callback_query(F.data == "gpt_finish")
async def gpt_finish_callback_handler(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.answer()
    await state.clear()
    await callback_query.message.answer("Розмову завершено. Повертаємось до головного меню...")
    await start(callback_query.message, bot)