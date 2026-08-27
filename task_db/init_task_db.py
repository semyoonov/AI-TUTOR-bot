import asyncpg
from dotenv import load_dotenv
from task_db.config_bd import DB_CONFIG, TABLE_NAMES

load_dotenv()

async def init_database():
    try:
        print("Подключаемся к PostgreSQL...")

        conn = await asyncpg.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database='postgres',
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )

        db_name = DB_CONFIG['database']
        exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", db_name)

        if not exists:
            await conn.execute(f"CREATE DATABASE {db_name}")
            print(f"База данных '{db_name}' создана")
        else:
            print(f"База данных '{db_name}' уже существует")

        await conn.close()
        print("postgres created successfully")

    except Exception as e:
        print(f"ОШИБКА: {type(e).__name__}: {e}")


async def create_task_tables():

    try:

        conn = await asyncpg.connect(**DB_CONFIG)

        await conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                task_number INTEGER NOT NULL, -- Номер задания ЕГЭ (4, 6, 15...)
                condition TEXT NOT NULL,
                image BYTEA,
                solution TEXT,
                answer TEXT,
                difficulty TEXT DEFAULT 'medium'
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_progress (
                user_id BIGINT,           -- Telegram ID
                task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
                is_correct BOOLEAN,
                solved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, task_id)
            )
        """)

        print('БД успешно инициализирована (Postgres)')

        await conn.close()
    except Exception as e:
        print(f"ОШИБКА: {type(e).__name__}: {e}")