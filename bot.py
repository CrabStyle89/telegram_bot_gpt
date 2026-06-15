import asyncio
from aiogram import Bot, Dispatcher

import credentials
from util import default_callback_handler
from handlers import main_router  # Імпортуємо наш збірний роутер

# Ініціалізація бота та диспетчера
bot = Bot(token=credentials.BOT_TOKEN)
dp = Dispatcher()

# Підключаємо всі хендлери з папки handlers
dp.include_router(main_router)


async def main():

    print("🤖 Бот успішно запущений з модульною структурою!")

    # Скидаємо накопичені повідомлення
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nБот зупинений користувачем. Бувай!")