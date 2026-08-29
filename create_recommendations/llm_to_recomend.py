#тоже цепочка (AI - агент по нашему через chain) - получает на вход строку из 7.1 оборачивает в Runnable интерфейес и с помощью промта загоняет в ллм. так то так наверно


# т.к. я решил возвращать список в select_in_db, то будет немного по другому
# from langchain_community.prompts import ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from config import MISTRAL_MODEL_NAME, MISTRAL_TOKEN
from promts import get_task_prompt
from create_recommendations.select_in_db import get_task_from_db

import json
import re
from langchain_core.output_parsers import StrOutputParser

llm = ChatMistralAI(
    api_key=MISTRAL_TOKEN,
    model=MISTRAL_MODEL_NAME
)

recommendation_chain = ChatPromptTemplate.from_template(get_task_prompt) | llm | StrOutputParser()

def parse_json(raw_text: str) -> dict:
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    json_str = match.group(0) if match else raw_text
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        cleaned = re.sub(r'\\(?![\\"])', r'\\\\', json_str)
        return json.loads(cleaned, strict=False)


async def get_task_recommendation(tg_id : int, user_query : str, filters : dict):
    tasks_from_db = await get_task_from_db(tg_user_id=tg_id, filters=filters)

    if not tasks_from_db:
        return {"condition": "Новых задач не нашлось.", "selected_task_id": None}

    text = "\n---\n".join([
        f"ID: {t['id']} | №{t['task_number']}\nУсловие: {t['condition']}" 
        for t in tasks_from_db
    ])

    try:
        raw =  await recommendation_chain.ainvoke({
            "query": user_query,
            "context": text
        })

        return parse_json(raw)
    except Exception as e:
        print(f"Mistral Error: {e}")
        return {"condition": "Ошибка ИИ", "selected_task_id": None}