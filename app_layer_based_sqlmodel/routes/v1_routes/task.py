from fastapi import APIRouter

from app_layer_based_sqlmodel.core.deps import TaskServiceDep
from app_layer_based_sqlmodel.models.task import TaskRead

router = APIRouter()
endpoint_name = "tasks"


@router.get("/{task_id}", summary="Get task", response_model=TaskRead)
async def get(*, service: TaskServiceDep, task_id: str):
    return await service.get_by_id(task_id)
