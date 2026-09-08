#память ученика: по каждому user_id храним человекочитаемый memory.md
#(статистика по номерам ЕГЭ + текущая незакрытая задача), плюс машиночитаемый JSON внутри того же файла

import json
import os
import re
from datetime import datetime

MEMORY_DIR = os.path.join(os.path.dirname(__file__), "data")
HISTORY_LIMIT = 15

_DATA_BLOCK_RE = re.compile(r"<!-- DATA\n```json\n(.*?)\n```\n-->", re.DOTALL)


def _memory_path(user_id: int) -> str:
    return os.path.join(MEMORY_DIR, f"{user_id}.md")


def _default_state() -> dict:
    return {"pending_task": None, "stats": {}, "history": []}


def load_state(user_id: int) -> dict:
    path = _memory_path(user_id)
    if not os.path.exists(path):
        return _default_state()

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        match = _DATA_BLOCK_RE.search(content)
        if not match:
            return _default_state()
        state = json.loads(match.group(1))
        state.setdefault("pending_task", None)
        state.setdefault("stats", {})
        state.setdefault("history", [])
        return state
    except Exception as e:
        print(f"Memory load error for user {user_id}: {e}")
        return _default_state()


def _render_markdown(user_id: int, state: dict) -> str:
    pending = state.get("pending_task")
    if pending:
        status = f"Ожидает проверки ответа на №{pending['task_number']} (id {pending['task_id']})."
    else:
        status = "Активной задачи нет."

    stats = state.get("stats", {})
    if stats:
        rows = []
        for task_number in sorted(stats.keys(), key=int):
            s = stats[task_number]
            solved = s["correct"] + s["incorrect"]
            accuracy = round(100 * s["correct"] / solved) if solved else 0
            rows.append(f"| {task_number} | {solved} | {s['correct']} | {s['incorrect']} | {accuracy}% |")
        table = (
            "| № задания | Решено | Верно | Неверно | Точность |\n"
            "|---|---|---|---|---|\n" + "\n".join(rows)
        )
    else:
        table = "Пока нет решённых задач."

    history = state.get("history", [])
    if history:
        history_lines = "\n".join(
            f"- {h['ts']} — №{h['task_number']} — {'верно' if h['is_correct'] else 'неверно'} "
            f"(ответ ученика: \"{h['user_answer']}\")"
            for h in reversed(history[-10:])
        )
    else:
        history_lines = "Пока нет истории попыток."

    data_json = json.dumps(state, ensure_ascii=False, indent=2)

    return f"""# Память ученика {user_id}

_Обновлено: {datetime.now().isoformat(timespec="seconds")}_

## Статус
{status}

## Статистика по номерам ЕГЭ
{table}

## Последние попытки
{history_lines}

<!-- DATA
```json
{data_json}
```
-->
"""


def save_state(user_id: int, state: dict) -> None:
    os.makedirs(MEMORY_DIR, exist_ok=True)
    path = _memory_path(user_id)
    with open(path, "w", encoding="utf-8") as f:
        f.write(_render_markdown(user_id, state))


def get_pending_task(user_id: int) -> dict | None:
    return load_state(user_id).get("pending_task")


def set_pending_task(user_id: int, task_id: int, task_number: int, answer: str, condition: str = "") -> None:
    state = load_state(user_id)
    state["pending_task"] = {
        "task_id": task_id,
        "task_number": task_number,
        "answer": answer,
        "condition": condition,
    }
    save_state(user_id, state)


def clear_pending_task(user_id: int) -> None:
    state = load_state(user_id)
    state["pending_task"] = None
    save_state(user_id, state)


def record_result(user_id: int, is_correct: bool, user_answer: str) -> dict:
    state = load_state(user_id)
    pending = state.get("pending_task")
    if not pending:
        return state

    task_number = str(pending["task_number"])
    stats = state.setdefault("stats", {})
    entry = stats.setdefault(task_number, {"correct": 0, "incorrect": 0})
    if is_correct:
        entry["correct"] += 1
    else:
        entry["incorrect"] += 1

    history = state.setdefault("history", [])
    history.append({
        "ts": datetime.now().isoformat(timespec="seconds"),
        "task_number": pending["task_number"],
        "task_id": pending["task_id"],
        "is_correct": is_correct,
        "user_answer": user_answer,
    })
    state["history"] = history[-HISTORY_LIMIT:]

    state["pending_task"] = None
    save_state(user_id, state)
    return state


def get_weak_task_numbers(user_id: int, min_attempts: int = 3) -> list[int]:
    stats = load_state(user_id).get("stats", {})
    candidates = []
    for task_number, s in stats.items():
        solved = s["correct"] + s["incorrect"]
        if solved >= min_attempts:
            accuracy = s["correct"] / solved
            candidates.append((accuracy, -solved, int(task_number)))
    candidates.sort()
    return [c[2] for c in candidates]


def format_context_for_llm(user_id: int) -> str:
    stats = load_state(user_id).get("stats", {})
    if not stats:
        return "Ученик ещё не решал задач — статистики пока нет."

    lines = []
    for task_number in sorted(stats.keys(), key=int):
        s = stats[task_number]
        solved = s["correct"] + s["incorrect"]
        accuracy = round(100 * s["correct"] / solved) if solved else 0
        lines.append(f"№{task_number}: {s['correct']}/{solved} верно ({accuracy}%)")
    return "; ".join(lines)
