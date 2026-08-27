#тут делим файл по чанкам, считает эмендинги и кладем в бд
#upd: пока что решил просто поделить с помощью markdown text splitter, по заголовкам

from langchain_text_splitters import MarkdownHeaderTextSplitter
from theory.init_vector_db import collection
import uuid


def insert_theory(file_path='theory/theory.md'):
    headers = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]

    md_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers,
        strip_headers=False
    )
    with open(file_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
    
    docs = md_splitter.split_text(md_text)

    documents = []
    metadatas = []
    ids = []

    for i, doc in enumerate(docs):
        documents.append(doc.page_content)
        metadatas.append(doc.metadata)
        ids.append(f"theory_chunk_{i}")

    collection.upsert(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    print(f"Успешно добавлено {len(documents)} чанков в документ.")