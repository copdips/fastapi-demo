from typing import TYPE_CHECKING

from app_domain_based_sqlalchemy.app_common.repositories import BaseRepository
from app_domain_based_sqlalchemy.app_task.models import Task, TaskStatus
from app_domain_based_sqlalchemy.app_task.schemas import TaskUpdate

if TYPE_CHECKING:
    import logging

    from sqlalchemy.ext.asyncio import AsyncSession


class TaskService(BaseRepository[Task]):
    def __init__(self, session: AsyncSession, logger: logging.Logger):
        super().__init__(session, Task, logger)

    async def update(self, task_id: str, new_data: TaskUpdate) -> Task:
        task = await self.get_by_id(task_id)
        task_data_dump = new_data.model_dump(exclude_unset=True)
        for key, value in task_data_dump.items():
            setattr(task, key, value)
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def set_status_to_done(self, task_id: str, message: str = "") -> Task:
        task_update = TaskUpdate(status=TaskStatus.done, message=message)
        return await self.update(task_id, task_update)

    async def set_status_to_failed(self, task_id: str, message: str) -> Task:
        task_update = TaskUpdate(status=TaskStatus.failed, message=message)
        return await self.update(task_id, task_update)
