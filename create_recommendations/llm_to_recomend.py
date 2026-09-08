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
    except Exception:
        pass

    try:
        cleaned = re.sub(r'\\(?![\\"/bfnrtu])', r'\\\\', json_str)
        return json.loads(cleaned, strict=False)
    except Exception:
        pass

    res = {}
    id_m = re.search(r'"selected_task_id":\s*(\d+)', raw_text)
    if id_m:
        res["selected_task_id"] = int(id_m.group(1))
    num_m = re.search(r'"task_number":\s*(\d+)', raw_text)
    if num_m:
        res["task_number"] = int(num_m.group(1))
    cond_m = re.search(r'"condition":\s*"(.*?)"', raw_text, re.DOTALL)
    if cond_m:
        res["condition"] = cond_m.group(1)
    return res


async def get_task_recommendation(tg_id : int, user_query : str, filters : dict, weak_hint : int | None = None, memory_context : str = ""):
    query_filters = dict(filters)
    if weak_hint and "task_number" not in filters:
        query_filters["task_number"] = weak_hint

    tasks_from_db = await get_task_from_db(tg_user_id=tg_id, filters=query_filters)

    # если под слабую тему не нашлось непройденных задач - пробуем без принудительного номера
    if not tasks_from_db and query_filters.get("task_number") != filters.get("task_number"):
        tasks_from_db = await get_task_from_db(tg_user_id=tg_id, filters=filters)

    if not tasks_from_db:
        return {"condition": "Новых задач не нашлось.", "selected_task_id": None}

    text = "\n---\n".join([
        f"ID: {t['id']} | №{t['task_number']}\nУсловие: {t['condition']}"
        for t in tasks_from_db
    ])

    try:
        raw = await recommendation_chain.ainvoke({
            "query": user_query,
            "context": text,
            "memory_hint": memory_context or "данных о прогрессе пока нет."
        })

        parsed = parse_json(raw)
        selected_id = parsed.get("selected_task_id")
        match = next((t for t in tasks_from_db if t["id"] == selected_id), None) if selected_id else None

        if match:
            parsed["answer"] = match["answer"]
            parsed["task_number"] = match["task_number"]
            hint = parsed.get("condition") or ""
            real_cond = match["condition"]
            if hint and hint != real_cond:
                parsed["condition"] = f"{hint}\n\n{real_cond}"
            else:
                parsed["condition"] = real_cond
            return parsed

        fallback = tasks_from_db[0]
        return {
            "task_number": fallback["task_number"],
            "condition": fallback["condition"],
            "selected_task_id": fallback["id"],
            "answer": fallback["answer"]
        }
    except Exception as e:
        print(f"Mistral Error: {e}")
        fallback = tasks_from_db[0]
        return {
            "task_number": fallback["task_number"],
            "condition": fallback["condition"],
            "selected_task_id": fallback["id"],
            "answer": fallback["answer"]
        }