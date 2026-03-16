# это общий конфиг сюда все по типу ключей и тегов
import os
from dotenv import load_dotenv
load_dotenv()

TG_TOKEN = os.getenv("TG_TOKEN")
MISTRAL_TOKEN = os.getenv("MISTRAL_TOKEN")
MISTRAL_MODEL_NAME = os.getenv("MISTRAL_MODEL_NAME")