"""01-5. 같은 질문을 제공자에 직접 보내기 vs Gateway를 거쳐 보내기

직접 호출은 제공자마다 주소·인증 헤더·요청 형식·응답 위치가 다르다.
Gateway 호출은 하나의 주소·키·형식으로 모델 이름만 바꾼다.
"""
import os
import statistics
import time

import httpx
from dotenv import load_dotenv

load_dotenv()
QUESTION = "한 단어로 답하세요: 맑은 하늘의 색은?"
GATEWAY = os.environ.get("LITELLM_BASE_URL", "http://localhost:4000")


def direct_openai():
    r = httpx.post(
        os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1") + "/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
        json={"model": "gpt-6-luna", "messages": [{"role": "user", "content": QUESTION}]},
        timeout=60,
    )
    return r.json()["choices"][0]["message"]["content"]


def direct_anthropic():
    r = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01"},
        json={"model": "claude-sonnet-5-5", "max_tokens": 100,
              "messages": [{"role": "user", "content": QUESTION}]},
        timeout=60,
    )
    return r.json()["content"][0]["text"]


def via_gateway(alias):
    r = httpx.post(
        f"{GATEWAY}/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['LITELLM_MASTER_KEY']}"},
        json={"model": alias, "messages": [{"role": "user", "content": QUESTION}]},
        timeout=60,
    )
    return r.json()["choices"][0]["message"]["content"]


CASES = [
    ("직접: OpenAI", direct_openai),
    ("직접: Anthropic", direct_anthropic),
    ("Gateway: fast", lambda: via_gateway("fast")),
    ("Gateway: smart", lambda: via_gateway("smart")),
]

for name, call in CASES:
    seconds, answer = [], None
    for _ in range(3):
        start = time.time()
        answer = call()
        seconds.append(time.time() - start)
    print(f"{name:18} 중앙값 {statistics.median(seconds):.2f}초  답: {answer.strip()}")
