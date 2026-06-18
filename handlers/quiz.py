from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from util import send_image, load_prompt, send_text_buttons, DialogStates, chat_gpt
from handlers.start import start
print("Модуль random.py успішно завантажено Python!")
router = Router()


# Обробник команди /quiz, використовую theme, замість відразу quiz, бо чомусь дефолтний хендлер
#  перехоплює керування інших, і не спраьовують ці при складній умові

@router.message(Command('quiz'))
async def quiz_cmd(message: Message,state: FSMContext):
    await state.clear()
    await send_image(message,'quiz')
    await send_text_buttons(
        message=message,
        text="Обери тему для квізу:",
        buttons={
            "theme_prog": "Програмування Python",
            "theme_math": "Математика",
            "theme_biology": "Біологія"
        }
    )

# Обробник вибору теми, фільтр такий щоб кнопка quiz_more не потрапила сюди на початку
@router.callback_query(F.data.startswith("theme_"))
async def quiz_select_theme_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    # Замість 'theme_prog' робим 'quiz_prog', бо саме ці слова очікує твій GPT-промпт!
    theme = callback_query.data.replace("theme_", "quiz_")

    # лічильник відповідей і кількості запитань
    await state.update_data(correct_answer=0, total_question=1)

    prompt = load_prompt("quiz")
    chat_gpt.set_prompt(prompt)

    await state.set_state(DialogStates.TEXT_QUIZ)
    await callback_query.message.answer("*Генерую перше питання... Зачекай секунду...*")

    question = await chat_gpt.add_message(theme)
    await callback_query.message.answer(question)

# Оброобник відповідей користувача в стані квізу
@router.message(DialogStates.TEXT_QUIZ)
async def quiz_answer_handler(message: Message, state: FSMContext):
    if message.text and message.text.startswith('/'):
        return

    user_answer = message.text
    gpt_evaluation = await chat_gpt.add_message(user_answer)

    # Поточна статистика
    user_data = await state.get_data()
    correct_answers = user_data.get('correct_answers', 0)
    total_questions = user_data.get('total_questions', 1)

    if gpt_evaluation.strip().startswith("Правильно!"):
        correct_answers += 1
        # Оновлюємо дані в пам'яті FSM
        await state.update_data(correct_answers=correct_answers)

    score_text = f"\n\n *Ваш рахунок: {correct_answers} з {total_questions}*"

    # Додаємо рахунок до відповіді бота
    full_response = gpt_evaluation + score_text

    await send_text_buttons(
        message=message,
        text=full_response,
        buttons={
            "quiz_more": "Наступне питання ➡",
            "quiz_finish": "Закінчити квіз ❌"
        }
    )

#Обробник кнопки Наступне питання
@router.callback_query(F.data == "quiz_more")
async def quiz_more_handler(callback_query: CallbackQuery,  state: FSMContext):
    await callback_query.answer()

    user_data = await state.get_data()
    total_questions = user_data.get('total_questions', 1) + 1
    await state.update_data(total_questions=total_questions)

    await callback_query.message.answer("*Генерую наступне питання...*")
    next_question = await chat_gpt.add_message("quiz_more")
    await callback_query.message.answer(next_question)

# Обробник кнопки зацінчити квіз
@router.callback_query(F.data == "quiz_finish")
async def quiz_finish_handler(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.answer()

    user_data = await state.get_data()
    correct_answers = user_data.get('correct_answers', 0)
    total_questions = user_data.get('total_questions', 1)

    await callback_query.message.answer(
        f" *Квіз завершено!*\n"
        f" Фінальний результат: *{correct_answers}* правильних відповідей з *{total_questions}*."
    )

    await state.clear()  # Очищаємо FSM стан
    await start(callback_query.message, bot)