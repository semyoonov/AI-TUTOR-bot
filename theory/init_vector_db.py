#инициализируем ВБД
import chromadb
from theory.init_emb_model import my_ef
from theory.config_vdb import CHROMA_DB_FOLDER

client = chromadb.PersistentClient(path=CHROMA_DB_FOLDER)
collection = client.get_or_create_collection(
    name="my_docs",
    embedding_function=my_ef
)
print("vdb инициализирована!")