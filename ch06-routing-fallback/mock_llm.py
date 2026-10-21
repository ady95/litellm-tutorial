"""06장·08장. 장애를 마음대로 일으키는 가짜 OpenAI 호환 서버

모델 이름으로 동작을 정한다.
  ok           바로 정상 응답
  ok-d500      500ms 뒤 정상 응답 (-d 뒤 숫자는 지연 ms)
  e429         항상 429 (Rate Limit)
  e500         항상 500
  flaky50      50% 확률로 500
  hang         응답하지 않고 오래 기다림 (타임아웃 시험용)

실행: uvicorn mock_llm:app --host 0.0.0.0 --port 8901
통계: GET /stats  초기화: POST /reset
"""
import asyncio
import json
import random
import re
import time
import uuid
from collections import Counter

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

app = FastAPI()
calls = Counter()


def completion_body(model, text):
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }


def error(status, message, headers=None):
    return JSONResponse(status_code=status, headers=headers,
                        content={"error": {"message": message, "type": "mock_error", "code": status}})


@app.post("/v1/chat/completions")
async def chat(request: Request):
    body = await request.json()
    model = body.get("model", "ok")
    calls[model] += 1

    delay = re.search(r"-d(\d+)", model)
    if delay:
        await asyncio.sleep(int(delay.group(1)) / 1000)
    if model.startswith("e429"):
        return error(429, "mock rate limit", {"retry-after": "1"})
    if model.startswith("e500"):
        return error(500, "mock server error")
    if model.startswith("flaky") and random.random() < int(re.search(r"flaky(\d+)", model).group(1)) / 100:
        return error(500, "mock flaky error")
    if model.startswith("hang"):
        await asyncio.sleep(600)

    text = f"mock answer from {model}"
    if body.get("stream"):
        async def events():
            chunk = completion_body(model, text)
            chunk["object"] = "chat.completion.chunk"
            chunk["choices"] = [{"index": 0, "delta": {"role": "assistant", "content": text}, "finish_reason": None}]
            yield f"data: {json.dumps(chunk)}\n\n"
            chunk["choices"] = [{"index": 0, "delta": {}, "finish_reason": "stop"}]
            yield f"data: {json.dumps(chunk)}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(events(), media_type="text/event-stream")
    return completion_body(model, text)


@app.get("/v1/models")
async def models():
    return {"object": "list", "data": [{"id": m, "object": "model"} for m in ("ok", "e429", "e500", "flaky50", "hang")]}


@app.get("/stats")
async def stats():
    return dict(calls)


@app.post("/reset")
async def reset():
    calls.clear()
    return {"reset": True}
