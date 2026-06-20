from aiogram import Router
from handlers import start, random, chat_gpt, talk, quiz, translate, recommend
from util import default_callback_handler

main_router = Router()

# Створюємо окремий роутер суворо для дефолтних речей, так як чомусь дефолтний роут
# перехоплює все підряд

fallback_router = Router()
fallback_router.callback_query.register(default_callback_handler)

# Підключаємо під-роутери у правильному порядку
main_router.include_router(start.router)
main_router.include_router(random.router)
main_router.include_router(chat_gpt.router)
main_router.include_router(talk.router)
main_router.include_router(quiz.router)
main_router.include_router(translate.router)
main_router.include_router(recommend.router)
main_router.include_router(fallback_router)