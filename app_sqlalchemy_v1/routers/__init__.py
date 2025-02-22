from .tag import router as tag_router
from .task import router as task_router
from .team import router as team_router
from .user import router as user_router

__all__ = ["tag_router", "task_router", "team_router", "user_router"]
