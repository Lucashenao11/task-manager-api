from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas import TaskCreate, TaskUpdate, TaskOut
from app.models import store

app = FastAPI(title="Task Manager API")


class APIError(Exception):
    def __init__(self, status_code: int, error: str, message: str):
        self.status_code = status_code
        self.error = error
        self.message = message


@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error, "message": exc.message},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "validation_error",
            "message": "Los datos enviados no son válidos",
            "details": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "internal_server_error", "message": "Ocurrió un error inesperado en el servidor"},
    )


@app.get("/health", status_code=status.HTTP_200_OK)
def health():
    return {"status": "ok"}


@app.get("/tasks", response_model=list[TaskOut], status_code=status.HTTP_200_OK)
def list_tasks():
    return store.list_all()


@app.get("/tasks/{task_id}", response_model=TaskOut, status_code=status.HTTP_200_OK)
def get_task(task_id: int):
    task = store.get(task_id)
    if task is None:
        raise APIError(status.HTTP_404_NOT_FOUND, "not_found", f"La tarea con id {task_id} no existe")
    return task


@app.post("/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate):
    if store.title_exists(data.title):
        raise APIError(status.HTTP_409_CONFLICT, "conflict", f"Ya existe una tarea con el título '{data.title}'")
    return store.create(data)


@app.put("/tasks/{task_id}", response_model=TaskOut, status_code=status.HTTP_200_OK)
def update_task(task_id: int, data: TaskUpdate):
    task = store.update(task_id, data)
    if task is None:
        raise APIError(status.HTTP_404_NOT_FOUND, "not_found", f"La tarea con id {task_id} no existe")
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    deleted = store.delete(task_id)
    if not deleted:
        raise APIError(status.HTTP_404_NOT_FOUND, "not_found", f"La tarea con id {task_id} no existe")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/debug/boom")
def boom():
    return 1 / 0  # error deliberado para demostrar el manejo del 500