# AI Tutor Bot (бот для подготовки к ЕГЭ по математике)

----
Telegram бот для подготовки к ЕГЭ по математике с фокусом на задания 4, 6 и 15. Использует RAG  для ответов на вопросы по теории и PostgreSQL для хранения задач.

## Возможности
- Ответы на теоретические вопросы по математике (задания 4, 6, 15)
- Выдача задач с решениями из базы данных
- RAG с векторной базой Chroma для поиска релевантной информации
- Поддержка Telegram с форматированием для мессенджера
- REST API на FastAPI со Swagger-документацией (`/docs`)

## Запуск

1. **Инициализация базы данных:**
```bash
docker compose --profile init up --build
```
Подождите завершения инициализации (увидите "Инициализация завершена успешно"). Первый раз выполняется долго (10 минут - норма).

2. **Запуск API и бота после инициализации:**
```bash
docker compose --profile main up --build
```

3. **Остановка:**
```bash
docker compose down
```

## Настройка

Создайте файл `.env` на основе `.env.example`:

```env
# Telegram и Mistral API
TG_TOKEN="your_telegram_bot_token"
MISTRAL_TOKEN="your_mistral_api_token"
MISTRAL_MODEL_NAME="mistral-small-latest"

# PostgreSQL
DB_HOST=db
DB_PORT=5432
DB_NAME=ai_tutor
DB_USER=postgres
DB_PASSWORD=your_password

# Chroma DB & Embedding model
HF_MODEL_NAME="ai-forever/sbert_large_nlu_ru"
CHROMA_DB_FOLDER="./chroma_db_folder"
```

## Структура проекта
- `api.py` — REST API бэкенд на FastAPI
- `bot.py` — Telegram-бот
- `task_db/` — работа с PostgreSQL и задачи
- `theory/` — векторная база Chroma и теория
- `rag.py` — RAG цепочка для ответов
- `docker-compose.yml` — конфигурация Docker


## Требования
- Python 3.11+
- PostgreSQL 16+
- Docker и Docker Compose (для Docker-варианта)
- Токены Mistral AI и Telegram Bot
