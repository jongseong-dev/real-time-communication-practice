import asyncio
import datetime
import json

import pytz
from fastapi import FastAPI, APIRouter
from starlette.responses import StreamingResponse

app = FastAPI()
router = APIRouter()


async def message_view(communicate_type: str):
    now = datetime.datetime.now(tz=pytz.timezone('Asia/Seoul'))
    now = now.strftime('%Y-%m-%d %H:%M:%S %Z')
    return f"{communicate_type} Message {now}"


@router.get("/polling", description="polling을 구현한 api")
async def polling():
    message = await message_view("Polling")
    return {"message": message}


event_msg = "Not Event"


@router.get("/long-polling", description="long-polling을 구현한 api")
async def long_polling():
    global event_msg
    while True:
        if event_msg != "Not Event":
            event_msg = "Not Event"
            message = await message_view("Long Polling")
            response_data = {"message": message}
            return response_data
        await asyncio.sleep(1)  # 동기 코드인 while 문이 event loop를 블로킹 시키기 때문에 논블로킹을 위한 비동기 코드 삽입


@router.post("/update", description="이벤트 변화를 위한 api")
async def update():
    global event_msg
    event_msg = "이벤트 변화 감지"
    return "OK"


@router.get("/sse", description="SSE를 구현한 api")
async def sse_endpoint():
    async def event_generator():
        while True:
            message = await message_view("SSE")
            message = {"message": message}
            yield f"data: {json.dumps(message)}\n\n"
            await asyncio.sleep(1)  # 1초마다 이벤트 전송

    return StreamingResponse(event_generator(), media_type="text/event-stream")
