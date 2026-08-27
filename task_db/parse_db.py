import asyncpg
from task_db.config_bd import DB_CONFIG, TABLE_NAMES

async def parse_tasks():
    folder_path = 'task_db/task_examples/'
    conn = await asyncpg.connect(**DB_CONFIG)

    for task_name in TABLE_NAMES:
        tasks_to_insert = []
        file_path = f"{folder_path}{task_name}.md"

        with open(file_path, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file if line.strip()]

            for i in range(0, len(lines) - 2, 3):
                task_text = lines[i + 1]
                answer_text = lines[i + 2]

                clean_task_number = int(''.join(filter(str.isdigit, task_name)))
                tasks_to_insert.append((clean_task_number, task_text, None, None, answer_text))
        query = """
            INSERT INTO tasks (task_number, condition, image, solution, answer)
            VALUES ($1, $2, $3, $4, $5)
        """

        if tasks_to_insert:
            await conn.executemany(query, tasks_to_insert)
            print(f'Data from (table {task_name}) successfully parsed')
        else:
            print(f"There's nothing to parse in the table {task_name}")

    await conn.close()