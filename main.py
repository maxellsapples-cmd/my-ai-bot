import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from duckduckgo_search import DDGS
from g4f.client import AsyncClient

TELEGRAM_TOKEN = "8999240956:AAFgn926seLAwCCmDpGrT5Tnks-qv7lv45s"

ai_client = AsyncClient()
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()


def search_internet(query: str) -> str:
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=3)]
            if not results:
                return "В интернете ничего не найдено."
            context = ""
            for i, res in enumerate(results, 1):
                context += f" Источник {i}: {res['title']} - {res['body']}\n"
            return context
    except Exception as e:
        print(f"Ошибка поиска: {e}")
        return "Не удалось выполнить поиск в интернете."


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я твой бесплатный ИИ-бот с поиском в Google. Задай мне любой вопрос!")


@dp.message()
async def handle_message(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")
    search_results = search_internet(message.text)
    prompt = (
        "Ты — умный ИИ-помощник. Ответь на вопрос пользователя, используя свежую информацию из интернета ниже.\n\n"
        f"Информация из сети:\n{search_results}\n\nВопрос: {message.text}"
    )
    try:
        response = await ai_client.chat.completions.create(
            model="llama-3.1-70b",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices.message.content
        await message.answer(answer)
    except Exception as e:
        await message.answer("Произошла ошибка при генерации ответа.")
        print(f"Ошибка ИИ: {e}")


async def main():
    logging.basicConfig(level=logging.INFO)
    print("Бот с поиском в интернете запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
