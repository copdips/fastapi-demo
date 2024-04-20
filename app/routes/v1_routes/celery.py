import asyncio

from celery.result import AsyncResult
from fastapi import APIRouter, WebSocket, status

from app.celery_tasks.tasks import (
    celery_task_q_high,
    celery_task_q_low,
)
from app.core.celery import celery_app
from app.models.celery_task import CeleryTaskCreate

router = APIRouter()
endpoint_name = "celery_tasks"


@router.post(
    "/low",
    summary="launch celery task in queue low",
    response_model=CeleryTaskCreate,
    status_code=status.HTTP_201_CREATED,
)
async def launch_celery_task_in_queue_low():
    result = celery_task_q_low.delay(  # pyright: ignore[reportFunctionMemberAccess]
        10,
    )
    return {"task_id": result.id}


@router.post(
    "/high",
    summary="launch celery task in queue high",
    response_model=CeleryTaskCreate,
    status_code=status.HTTP_201_CREATED,
)
async def launch_celery_task_in_queue_high():
    result = celery_task_q_high.delay(  # pyright: ignore[reportFunctionMemberAccess]
        10,
    )
    return {"task_id": result.id}


# websocket client: tools/celery_task_result_websocket_client.py
@router.websocket("/ws/{task_id}")
async def query_task_result(websocket: WebSocket, task_id: str):
    await websocket.accept()

    result = AsyncResult(task_id, app=celery_app)
    while not result.ready():
        await websocket.send_text(result.state)
        await asyncio.sleep(1)

    if result.successful():
        await websocket.send_text(str(result.state))
        await websocket.send_text(str(result.result))
    else:
        await websocket.send_text(result.state)
        exception_message = str(result.result)
        traceback = result.traceback
        msg = (
            "Task failed due to an exception.\n"
            f"Exception message: {exception_message}\n"
            f"Traceback: {traceback}"
        )
        await websocket.send_text(msg)
    await websocket.close()
