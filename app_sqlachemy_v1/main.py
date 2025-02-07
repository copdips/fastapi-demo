from app_sqlachemy_v1.core.db import init_db
from fastapi import FastAPI
from app_sqlachemy_v1.routers import tag_router, team_router, user_router

app = FastAPI(title="FastAPI Demo")

# Include routers
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(team_router, prefix="/teams", tags=["teams"])
app.include_router(tag_router, prefix="/tags", tags=["tags"])


@app.on_event("startup")
async def on_startup():
    # Create tables on startup
    await init_db()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
