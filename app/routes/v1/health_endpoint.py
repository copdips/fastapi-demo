from fastapi import APIRouter, Depends, Response
from sqlalchemy.exc import OperationalError
from sqlmodel import text

from app.core.deps import get_db_session
from app.db.models.health_models import HealthRead
from app.settings import settings

router = APIRouter()
endpoint_name = "health"


@router.get(
    "/",
    summary="Get API health status",
    response_model=HealthRead,
)
async def get_health(
    response: Response,
    db_session=Depends(get_db_session),
):
    response.headers["Cache-Control"] = "no-cache"
    meta = {"api_version": settings.api_version}
    try:
        await db_session.execute(text("SELECT 1"))
        # from api.db.models import User
        # user = await db_session.get(User, 1)
    except OperationalError as ex:
        response.status_code = 503
        return HealthRead(
            status="error",
            message=str(ex),
            meta=meta,
        )
    else:
        return HealthRead(
            status="ok",
            message="Database is running",
            meta=meta,
        )