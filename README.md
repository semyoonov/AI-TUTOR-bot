# AI Tutor Bot (бот для подготовки к ЕГЭ по математике)

info: *Бот находится в разработке, поэтому могут быть ошибки*
----
Telegram бот для подготовки к ЕГЭ по математике с фокусом на задания 4, 6 и 15. Использует RAG  для ответов на вопросы по теории и PostgreSQL для хранения задач.

## Возможности
- Ответы на теоретические вопросы по математике (задания 4, 6, 15)
- Выдача задач с решениями из базы данных
- RAG с векторной базой Chroma для поиска релевантной информации
- Поддержка Telegram с форматированием для мессенджера

## Запуск

### Вариант 1: Через Docker

1. **Инициализация базы данных:**
```bash
docker-compose --profile init up --build
```
Подождите завершения инициализации (увидите "Инициализация завершена успешно"). Первый раз выполняется долго (10 минут - норма).

2. **Запуск бота после инициализации:**
```bash
docker-compose --profile main up --build
```

3. **Остановка:**
```bash
docker-compose down
```

### Вариант 2: Через Python

1. **Запуск PostgreSQL:**
```bash
docker run --name ai_tutor_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=ai_tutor \
  -p 5432:5432 \
  -d postgres
```

2. **Настройка окружения:**
```bash
pip install -r req.txt
cp .env.example .env
# Отредактируйте .env с вашими токенами
```

3. **Инициализация баз данных:**
```bash
python init_db.py
```

4. **Запуск бота:**
```bash
python bot.py
```

## Настройка

Создайте файл `.env` на основе `.env.example`:

```env
# Telegram и Mistral API
TG_TOKEN="your_telegram_bot_token"
MISTRAL_TOKEN="your_mistral_api_token"
MISTRAL_MODEL_NAME="mistral-small-latest"

# PostgreSQL
DB_HOST=localhost  # или db для Docker
DB_PORT=5432
DB_NAME=ai_tutor
DB_USER=postgres
DB_PASSWORD=your_password

# Chroma DB
HF_MODEL_NAME="ai-forever/sbert_large_nlu_ru"
CHROMA_DB_FOLDER="./chroma_db_folder"
```

## Структура проекта
- `bot.py` — основной файл бота
- `task_db/` — работа с PostgreSQL и задачи
- `theory/` — векторная база Chroma и теория
- `rag.py` — RAG цепочка для ответов
- `docker-compose.yml` — конфигурация Docker

## Заметки разработки
- Используется Chroma для векторного поиска по теории
- PostgreSQL для хранения задач и прогресса пользователей
- LangChain для работы с LLM (Mistral)
- RAG реализован через retriever + prompt template
- Задания разбиты по чанкам по заголовкам для лучшего поиска

## Требования
- Python 3.11+
- PostgreSQL 16+
- Docker и Docker Compose (для Docker-варианта)
- Токены Mistral AI и Telegram Bot