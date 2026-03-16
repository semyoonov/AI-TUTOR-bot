#тут параметры и пути подключения в векторной бд
import os
from dotenv import load_dotenv
load_dotenv()

HF_MODEL_NAME = os.getenv("HF_MODEL_NAME")
CHROMA_DB_FOLDER = os.getenv("CHROMA_DB_FOLDER")