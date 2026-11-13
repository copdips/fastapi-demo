from fastapi import APIRouter

router = APIRouter()
endpoint_name = "sentry_demo"


@router.get("/sentry-debug")
async def trigger_error():
    _ = 1 / 0
