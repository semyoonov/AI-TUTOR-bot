#тут бот (может еще сайт напишем, но не факт)
#тут хватит одного файла это просто обычный бот в тг будет он будет брать все функции из других папок по большей части

import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode

from langchain_core.prompts import PromptTemplate
from langchain_mistralai import ChatMistralAI
from langchain_core.output_parsers import JsonOutputParser

from rag import get_rag_answer
from create_recommendations.llm_to_recomend import get_task_recommendation
from config import TG_TOKEN, MISTRAL_MODEL_NAME, MISTRAL_TOKEN
from promts import ROUTER_PROMPT

llm = ChatMistralAI(api_key=MISTRAL_TOKEN, model=MISTRAL_MODEL_NAME)
router_template = PromptTemplate.from_template(ROUTER_PROMPT)
router_chain = router_template | llm | JsonOutputParser()

bot = Bot(token=TG_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message : types.Message):
    await message.answer("Бот запущен. Что изучаем сегодня?")

@dp.message()
async def handle_message(message : types.Message):
    user_query = message.text
    tg_id = message.from_user.id

    try:
        routing_data = await router_chain.ainvoke({"query": user_query})
        intent = str(routing_data.get("intent", "THEORY")).upper()

        raw_filters = {
            "task_number": routing_data.get("task_number"),
            "difficulty": routing_data.get("difficulty")
        }

        filters = {k: v for k, v in raw_filters.items() if v is not None}
        loop = asyncio.get_event_loop()

        if "THEORY" in intent:
            print("+THEORY")
            response = await loop.run_in_executor(None, get_rag_answer, user_query)
            await message.answer(response)    
        else:
            print("+TASK")
            response = await loop.run_in_executor(None, get_task_recommendation, tg_id, user_query, filters)

            if isinstance(response, dict):
                num = response.get('task_number', '??')
                cond = response.get('condition', 'Условие не найдено.')
                
                full_text = f"📝 Задача №{num}\n\n{cond}"
                await message.answer(full_text)
            else:
                await message.answer(response) 
    except Exception as e:
        print(f"Ошибка в боте: {e}")
        await message.answer("Произошла ошибка. Попробуй позже.")

async def main():
    print("--- Бот успешно запущен и готов к работе ---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())