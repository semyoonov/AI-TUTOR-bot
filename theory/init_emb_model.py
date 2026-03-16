from sentence_transformers import SentenceTransformer
from langchain_core.embeddings import Embeddings
from theory.config_vdb import HF_MODEL_NAME

class My_embeddings(Embeddings):
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name, device='cpu')

    def embed_documents(self, texts):
        return self.model.encode(texts).tolist()

    def embed_query(self, text):
        return self.model.encode(text).tolist()

    def __call__(self, input):
        return self.model.encode(input).tolist()

    def name(self) -> str:
        return "my_model"

my_ef = My_embeddings(HF_MODEL_NAME)
print("Модель инициализирована!")