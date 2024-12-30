import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from main import chek_news_update
from utils import logger

# Создаем бота и диспетчер
bot = Bot(token="7314617584:AAF0yoHEm5bfzgZ8_PoVZkJSM-UYRy1JG3Q")
dp = Dispatcher()
router = Router()  # Используем роутер

# Словарь для хранения ID пользователей
subscribed_users = set()


@router.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    subscribed_users.add(user_id)
    await message.reply("Вы подписались на новые уведомления!")


async def news_every_minute():
    while True:
        fresh_new = chek_news_update()

        if fresh_new:
            for user_id in subscribed_users:
                for item in fresh_new:
                    news = "\n".join(item)
                    await bot.send_message(user_id, news)

        await asyncio.sleep(3600)  # Ждем 1 час


# Главная функция
async def main():
    dp.include_router(router)
    loop = asyncio.get_event_loop()
    loop.create_task(news_every_minute())
    await dp.start_polling(bot)


if __name__ == "__main__":
    logger.info('Bot запущен')
    asyncio.run(main())
