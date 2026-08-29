from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from rag import get_rag_answer
from create_recommendations.llm_to_recomend import get_task_recommendation
from config import TG_TOKEN, MISTRAL_MODEL_NAME, MISTRAL_TOKEN
from promts import ROUTER_PROMPT

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

        if "THEORY" in intent:
            print("+THEORY")
            response = await get_rag_answer(user_query)
            return response    
        else:
            print("+TASK")
            response = await get_task_recommendation(tg_id, user_query, filters)

            if isinstance(response, dict):
                num = response.get('task_number', None)
                cond = response.get('condition', 'Условие не найдено.')

                full_text = f"📝 **Задача №{num}**\n\n{cond}" if num else cond
                return full_text
            else:
                return response 
    except Exception as e:
        print(f"Ошибка в API: {e}")
        return "Произошла ошибка. Попробуй позже."

if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)