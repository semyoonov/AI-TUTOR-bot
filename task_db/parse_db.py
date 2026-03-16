import psycopg2
from task_db.config_bd import DB_CONFIG, TABLE_NAMES

def parse_tasks():
    folder_path = 'task_db/task_examples/'
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

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
            VALUES (%s, %s, %s, %s, %s)
        """

        if tasks_to_insert:
            cursor.executemany(query, tasks_to_insert)
            conn.commit()
            print(f'Data from (table {task_name}) successfully parsed')
        else:
            print(f"There's nothing to parse in the table {task_name}")
    cursor.close()
    conn.close()

# if __name__ == "__main__":
#     parse_tasks()