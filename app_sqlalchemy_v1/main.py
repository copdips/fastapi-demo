from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from sqladmin import Admin, ModelView

from app_sqlalchemy_v1.core.db import engine, init_db
from app_sqlalchemy_v1.models.user import User
from app_sqlalchemy_v1.routers import tag_router, task_router, team_router, user_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="FastAPI Demo", lifespan=lifespan)


@app.middleware("http")
async def remove_trailing_slash(request: Request, call_next):
    if request.url.path.endswith("/") and request.url.path != "/":
        return RedirectResponse(url=request.url.path.rstrip("/"), status_code=308)
    return await call_next(request)


# Include routers
app.include_router(task_router, prefix="/tasks", tags=["tasks"])
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(team_router, prefix="/teams", tags=["teams"])
app.include_router(tag_router, prefix="/tags", tags=["tags"])

admin = Admin(app, engine)


class UserAdmin(ModelView, model=User):
    column_list = [c_attr.key for c_attr in User.__mapper__.column_attrs]
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True


admin.add_view(UserAdmin)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
