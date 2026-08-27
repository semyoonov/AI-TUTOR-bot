#инициализация баз данных
import asyncio
async def init_db():
    try:
        from task_db.init_task_db import init_database, create_task_tables
        from task_db.parse_db import parse_tasks
        from theory.chunking_embending_insert import insert_theory
        
        await init_database()
        await create_task_tables()
        await parse_tasks()
        insert_theory()
        print("Инициализация завершена успешно")
    except Exception as e:
        print(f"Ошибка при инициализации: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_db())