from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.exc import OperationalError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app_domain_based.app_common.deps import get_db_session
from app_domain_based.app_health.schemas import HealthRead

router = APIRouter()
endpoint_name = "health"


@router.get(
    "",
    summary="Get API health status",
    response_model=HealthRead,
)
async def get_health(
    req: Request,
    response: Response,
    # ! better to create a dedicated health_service instead of direct db_session
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
):
    response.headers["Cache-Control"] = "no-cache"
    meta = {
        "api_version": req.app.state.settings.api_version,
        "db_engine": db_session.bind.engine.name,
    }
    try:
        res = await db_session.exec(select(1))
    except OperationalError as ex:
        response.status_code = 503
        return HealthRead(
            status="error",
            message=str(ex),
            meta=meta,
        )

    else:
        if res.all() != [1]:
            response.status_code = 503
            return HealthRead(
                status="error",
                message="Got unexpected result from the database",
                meta=meta,
            )
        return HealthRead(
            status="ok",
            message="Database is running",
            meta=meta,
        )
