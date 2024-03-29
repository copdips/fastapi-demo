import logging

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.base_models import TaskStatus
from app.models.db_models import Task
from app.models.task_model import TaskUpdate
from app.services.base_service import BaseService


class TaskService(BaseService):
    def __init__(self, session: AsyncSession, logger: logging.Logger):
        super().__init__(session, Task, logger)

    async def update(self, task_id: str, new_data: TaskUpdate) -> Task:
        task = await self.get_by_id(task_id)
        task_data_dump = new_data.model_dump(exclude_unset=True)
        task.sqlmodel_update(task_data_dump)
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task  # pyright: ignore[reportReturnType]

    async def set_status_to_done(self, task_id: str, message: str = "") -> Task:
        task_update = TaskUpdate(status=TaskStatus.done, message=message)
        return await self.update(task_id, task_update)

    async def set_status_to_failed(self, task_id: str, message: str) -> Task:
        task_update = TaskUpdate(status=TaskStatus.failed, message=message)
        return await self.update(task_id, task_update)
