#инициализация баз данных
def init_db():
    try:
        from task_db.init_task_db import init_database, create_task_tables
        from task_db.parse_db import parse_tasks
        import theory.chunking_embending_insert
        
        init_database()
        create_task_tables()
        parse_tasks()
        print("Инициализация завершена успешно")
    except Exception as e:
        print(f"Ошибка при инициализации: {e}")
        raise

if __name__ == "__main__":
    init_db()