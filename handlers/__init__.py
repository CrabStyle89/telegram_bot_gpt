from aiogram import Router
# Замінюємо відносні імпорту на абсолютні від кореня проекту
from handlers import start, random, chat_gpt, talk, quiz, translate
from util import default_callback_handler

main_router = Router()

# Створюємо окремий роутер суворо для дефолтних речей
fallback_router = Router()
fallback_router.callback_query.register(default_callback_handler)

# Підключаємо під-роутери у правильному порядку
main_router.include_router(start.router)
main_router.include_router(random.router)
main_router.include_router(chat_gpt.router)
main_router.include_router(talk.router)
main_router.include_router(quiz.router)
main_router.include_router(translate.router)
# Суворо НАЙОСТАННІМ підключаємо дефолтний роутер
main_router.include_router(fallback_router)