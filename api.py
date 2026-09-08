from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from rag import get_rag_answer
from create_recommendations.llm_to_recomend import get_task_recommendation
from config import TG_TOKEN, MISTRAL_MODEL_NAME, MISTRAL_TOKEN
from promts import ROUTER_PROMPT
from answer_checker import check_answer
from memory.user_memory import (
    get_pending_task,
    set_pending_task,
    record_result,
    get_weak_task_numbers,
    format_context_for_llm,
)

from langchain_core.prompts import PromptTemplate
from langchain_mistralai import ChatMistralAI
from langchain_core.output_parsers import JsonOutputParser

app = FastAPI(title="AI-tutor API")

class ChatRequest(BaseModel):
    user_id : int
    message : str

class TheoryRequest(BaseModel):
    query : str

class TaskRequest(BaseModel):
    user_id : int
    query : str
    task_number : int | None = None
    difficulty : str | None = None

llm = ChatMistralAI(api_key=MISTRAL_TOKEN, model=MISTRAL_MODEL_NAME)
router_template = PromptTemplate.from_template(ROUTER_PROMPT)
router_chain = router_template | llm | JsonOutputParser()

@app.post("/api/chat")
async def chat(req : ChatRequest):
    user_query = req.message
    tg_id = req.user_id

    try:
        routing_data = await router_chain.ainvoke({"query": user_query})
        intent = str(routing_data.get("intent", "THEORY")).upper()

        raw_filters = {
            "task_number": routing_data.get("task_number"),
            "difficulty": routing_data.get("difficulty")
        }

        filters = {k: v for k, v in raw_filters.items() if v is not None}

        pending_task = get_pending_task(tg_id)

        if "ANSWER" in intent and pending_task:
            print("+ANSWER")
            is_correct = await check_answer(pending_task["answer"], user_query)
            record_result(tg_id, is_correct, user_query)

            if is_correct:
                return f"✅ Верно! Правильный ответ: {pending_task['answer']}"
            else:
                return (
                    f"❌ Неверно. Правильный ответ: {pending_task['answer']}.\n"
                    "Не расстраивайся, потренируемся на этой теме ещё."
                )

        if "THEORY" in intent:
            print("+THEORY")
            response = await get_rag_answer(user_query)
            return response
        else:
            print("+TASK")
            weak_numbers = get_weak_task_numbers(tg_id)
            weak_hint = weak_numbers[0] if weak_numbers and not filters.get("task_number") else None
            memory_context = format_context_for_llm(tg_id)

            response = await get_task_recommendation(
                tg_id, user_query, filters,
                weak_hint=weak_hint, memory_context=memory_context
            )

            if isinstance(response, dict):
                num = response.get('task_number', None)
                cond = response.get('condition', 'Условие не найдено.')
                task_id = response.get('selected_task_id')
                answer = response.get('answer')

                if task_id and answer:
                    set_pending_task(tg_id, task_id=task_id, task_number=num, answer=answer, condition=cond)

                full_text = f"📝 **Задача №{num}**\n\n{cond}" if num else cond
                return full_text
            else:
                return response
    except Exception as e:
        print(f"Ошибка в API: {e}")
        return "Произошла ошибка. Попробуй позже."

if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)