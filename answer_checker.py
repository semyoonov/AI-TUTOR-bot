#цепочка, которая сверяет ответ ученика с правильным ответом задачи через LLM
#(нужна LLM, а не строковое сравнение, т.к. один и тот же ответ можно записать по-разному: "0.5", "0,5", "1/2")
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from langchain_core.output_parsers import JsonOutputParser
from config import MISTRAL_MODEL_NAME, MISTRAL_TOKEN
from promts import CHECK_ANSWER_PROMPT

llm = ChatMistralAI(api_key=MISTRAL_TOKEN, model=MISTRAL_MODEL_NAME)
check_chain = ChatPromptTemplate.from_template(CHECK_ANSWER_PROMPT) | llm | JsonOutputParser()


async def check_answer(correct_answer: str, user_answer: str) -> bool:
    try:
        result = await check_chain.ainvoke({
            "correct_answer": correct_answer,
            "user_answer": user_answer
        })
        return bool(result.get("is_correct"))
    except Exception as e:
        print(f"Answer check error: {e}")
        return False
