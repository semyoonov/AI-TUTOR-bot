import psycopg2
from dotenv import load_dotenv
from task_db.config_bd import DB_CONFIG, TABLE_NAMES

load_dotenv()

def init_database():
    try:
        print("Подключаемся к PostgreSQL...")

        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database='postgres',
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )

        conn.autocommit = True
        cursor = conn.cursor()
        print("Подключение успешно")

        db_name = DB_CONFIG['database']
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"База данных '{db_name}' создана")
        else:
            print(f"База данных '{db_name}' уже существует")

        cursor.close()
        conn.close()
        print("postgres created successfully")

    except Exception as e:
        print(f"ОШИБКА: {type(e).__name__}: {e}")


def create_task_tables():

    try:

        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("""
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

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_progress (
                user_id BIGINT,           -- Telegram ID
                task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
                is_correct BOOLEAN,
                solved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, task_id)
            )
        """)

        print('БД успешно инициализирована (Postgres)')

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"ОШИБКА: {type(e).__name__}: {e}")

# if __name__ == "__main__":
#     init_database()
#     create_task_tables()