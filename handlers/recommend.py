from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from util import send_image, load_prompt, send_text_buttons, DialogStates, chat_gpt
from handlers.start import start

router = Router()

# Обробник команди /recommend
@router.message(Command('recommend'))
async def recommend(message: Message, state: FSMContext):
    await state.clear()
    await send_image(message, 'recommend')

    #вибір категорій
    await send_text_buttons(
        message=message,
        text = "Оберіть категорію що саме Ви шукаєте",
        buttons={
            "rec_cat_films": "Фільми",
            "rec_cat_books": "Книги",
            "rec_cat_musics": "Музика",
            "rec_cat_anime" : "Аніме",
            "rec_cat_dorams": "Дорами"
        })

    # Обробник вибору категорії

@router.callback_query(F.data.startswith("rec_cat_"))
async def rec_select_category_handler(callback_query:CallbackQuery, state: FSMContext):
    await callback_query.answer()
    category = callback_query.data.replace("rec_cat_", "")
    await state.update_data(category=category, blacklist=[])
    await state.set_state(DialogStates.REC_WAITING)
    await callback_query.message.answer(f"Обрано {category}! Напиши мені бажаний жанр")

# Обробник вибору жанру, генерація рекомендації
@router.message(DialogStates.REC_WAITING)
async def rec_genre_handler(message: Message, state: FSMContext):
    if message.text and message.text.startswith('/'):
        return
    genre = message.text
    await state.update_data(genre=genre)
    await message.answer("...підбираю найкращі варіанти")
    await generate_recomendation(message, state)

# Генератор рекомендацій
async def generate_recomendation(message: Message, state: FSMContext):
    user_data = await state.get_data()
    category = user_data.get("category")
    blacklist = user_data.get("blacklist", [])
    genre = user_data.get("genre")
    prompt = load_prompt("recommend")

    gpt_query = f"Порекомендуй твір з категорії: {category}, у жанрі: {genre}"

    if blacklist:
        ignored_titles = ", ".join(blacklist)
        gpt_query += f"Важливо: Користувачеві НЕ подобаються і він вже бачив ці твори, тому НЕ РЕКОМЕНДУЙ їх: {ignored_titles}"

    recommendation = await chat_gpt.send_question(prompt, gpt_query)
    await state.update_data(current_rec=recommendation)
    await state.set_state(DialogStates.REC_VIEWING)
    await send_text_buttons(
        message=message,
        text=recommendation,
        buttons={
            "rec_dislike":"Не подобається",
            "rec_finish":"Закінчити"
        }
    )

# Обробник кнопки "не подобається"
@router.callback_query(F.data== "rec_dislike")
async def rec_dislike_handler(callback_query:CallbackQuery, state: FSMContext):
    await callback_query.answer()
    user_data = await state.get_data()
    blacklist = user_data.get("blacklist", [])
    current_rec = user_data.get("current_rec", "")

    # беремо перші 50 символів з рекомендації, там має бути назва твору
    short_title = current_rec.split('\n')[0][:50]
    if short_title and short_title not in blacklist:
        blacklist.append(short_title)
        await state.update_data(blacklist=blacklist)
    await callback_query.answer("Зрозумів, це викреслюємо. Шукаю інший варіант...")
    await generate_recomendation(callback_query.message, state)

# Обробник кнопки закінчити
@router.callback_query(F.data== "rec_finish")
async def rec_finish_handler(callback_query:CallbackQuery, state: FSMContext, bot:Bot):
    await callback_query.answer()
    await state.clear()
    await callback_query.message.answer("Пошук завершено")
    await start(callback_query.message, bot)