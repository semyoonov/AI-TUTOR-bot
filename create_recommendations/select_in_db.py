#извлекаем из бдшки инофрмацию по человеку и переводим это в строку
#(на вопрос как это будет выглядеть я не знаю)


#я решил возвращать список задач. каждая задача - кортеж
from task_db.config_bd import DB_CONFIG
import psycopg2

def get_task_from_db(tg_user_id, filters: dict, limit = 5):

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = """
            SELECT id, task_number, condition, difficulty 
                FROM tasks t
                WHERE NOT EXISTS (
                    SELECT 1 FROM user_progress up 
                    WHERE up.task_id = t.id AND up.user_id = %s
            )
        """

        params = [tg_user_id]

        if filters.get("task_number"):
            query += " AND t.task_number = %s"
            params.append(filters["task_number"])
        
        if filters.get("difficulty"):
            query += " AND t.difficulty = %s"
            params.append(filters["difficulty"])
        
        query += " ORDER BY RANDOM() LIMIT %s"
        params.append(limit)

        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    except Exception as e:
        print(f"SQL Error: {e}")
        return []