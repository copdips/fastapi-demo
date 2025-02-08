from .user import router as user_router
from .team import router as team_router
from .tag import router as tag_router

__all__ = ["user_router", "team_router", "tag_router"]
