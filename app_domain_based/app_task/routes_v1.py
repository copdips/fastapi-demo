import asyncio
from time import sleep

from fastapi import APIRouter, BackgroundTasks
from fastapi.concurrency import run_in_threadpool

router = APIRouter()


async def higher_task():
    await run_in_threadpool(task)


async def task():
    print("first sync sleep")
    sleep(5)
    print("first async sleep")
    await asyncio.sleep(5)
    print("2nd sync sleep")
    sleep(5)
    print("Task is done")


@router.get("/")
async def run_task(background_tasks: BackgroundTasks):
    background_tasks.add_task(higher_task)
    return {}
