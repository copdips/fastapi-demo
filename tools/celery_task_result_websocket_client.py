"""use websocket to query celery task result:
ipy /home/xiang/git/fastapi-demo/tools/celery_task_result_websocket_client.py {task_id}
ref: https://medium.com/@youssefchamrah/empowering-applications-with-asynchronous-magic-the-celery-fastapi-docker-and-flower-ac119efc2e04
"""

import asyncio

import websockets
from websockets.exceptions import ConnectionClosed


async def consume_websocket(task_id: str):
    ws_url = f"ws://localhost:8000/v1/celery_tasks/ws/{task_id}"
    try:
        async with websockets.connect(ws_url) as websocket:
            while True:
                response = await websocket.recv()
                print(f"Received message: {str(response)}")
                if response == "SUCCESS":
                    print("Got success response")
                    break
            response = await websocket.recv()
            print("result:", response)
    except ConnectionClosed as ex:
        if ex.code == 1000:
            print("Connection closed normally.")
        else:
            print(f"Connection closed with error: {ex}")
    except Exception as ex:
        print(f"Unhandled error: {ex}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Please provide task id")
        sys.exit(1)

    task_id = sys.argv[1]
    try:
        asyncio.run(consume_websocket(task_id))
    except Exception as ex:
        print(f"Fail with error: {ex}")
