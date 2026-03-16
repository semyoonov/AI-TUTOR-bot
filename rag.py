#тут будет цепочка(langchain) который будет обращаться в нашу векторную бд с промтом
from langchain_mistralai import ChatMistralAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from promts import get_theory_prompt

from theory.init_emb_model import my_ef
from theory.config_vdb import CHROMA_DB_FOLDER
from config import MISTRAL_TOKEN, MISTRAL_MODEL_NAME

vector_db = Chroma(
    persist_directory=CHROMA_DB_FOLDER,
    embedding_function=my_ef,
    collection_name="my_docs"
)

retriever = vector_db.as_retriever(search_kwargs={"k": 5})
llm = ChatMistralAI(
    model=MISTRAL_MODEL_NAME,
    api_key=MISTRAL_TOKEN,
    temperature=0.1
)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

prompt = ChatPromptTemplate.from_template(get_theory_prompt)
chain = (
    {
        "context": retriever | format_docs,
        "question" : RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)

def get_rag_answer(query):
    return chain.invoke(query)