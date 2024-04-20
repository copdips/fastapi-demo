from fastapi import APIRouter, status

from app.models.taskiq_task import TaskiqTaskCreate
from app.taskiq_tasks.tasks import (
    taskiq_task_q_low,
)

router = APIRouter()
endpoint_name = "taskiq_tasks"


@router.post(
    "/low",
    summary="launch taskiq task in queue low",
    response_model=TaskiqTaskCreate,
    status_code=status.HTTP_201_CREATED,
)
async def launch_taskiq_task_in_queue_low():
    result = await taskiq_task_q_low.kiq(10)
    return {"task_id": result.task_id}
