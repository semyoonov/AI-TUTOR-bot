from init_task_db import init_database, create_task_tables
from parse_db import parse_tasks

if __name__ == "__main__":
    init_database()
    create_task_tables()
    parse_tasks()