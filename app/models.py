from app.schemas import TaskCreate, TaskUpdate

class TaskStore:
    def __init__(self):
        self._tasks: dict[int, dict] = {}
        self._next_id = 1

    def list_all(self) -> list[dict]:
        return list(self._tasks.values())

    def get(self, task_id: int) -> dict | None:
        return self._tasks.get(task_id)

    def title_exists(self, title: str) -> bool:
        return any(t["title"] == title for t in self._tasks.values())

    def create(self, data: TaskCreate) -> dict:
        task = {"id": self._next_id, "title": data.title, "done": data.done}
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task

    def update(self, task_id: int, data: TaskUpdate) -> dict | None:
        if task_id not in self._tasks:
            return None
        self._tasks[task_id] = {"id": task_id, "title": data.title, "done": data.done}
        return self._tasks[task_id]

    def delete(self, task_id: int) -> bool:
        if task_id not in self._tasks:
            return False
        del self._tasks[task_id]
        return True

store = TaskStore()