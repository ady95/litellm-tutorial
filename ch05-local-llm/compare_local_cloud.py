"""05-4. 같은 클라이언트로 로컬·클라우드 모델 비교하기"""
import json
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.environ.get("LITELLM_BASE_URL", "http://localhost:4000"),
    api_key=os.environ["LITELLM_MASTER_KEY"],
)
ALIASES = ["local-small", "local", "fast", "smart"]
WEATHER_TOOL = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "도시의 현재 날씨를 조회한다",
        "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
    },
}

print(f"{'별칭':12} {'지연':>6} {'출력':>5} {'비용(USD)':>10}  도구 호출        답변")
for alias in ALIASES:
    start = time.time()
    raw = client.chat.completions.with_raw_response.create(
        model=alias,
        messages=[{"role": "user", "content": "RAG와 파인튜닝의 차이를 한 문장으로 설명하세요."}],
    )
    seconds = time.time() - start
    answer = raw.parse()
    cost = float(raw.headers.get("x-litellm-response-cost") or 0)

    tool_response = client.chat.completions.create(
        model=alias,
        messages=[{"role": "user", "content": "서울 날씨 알려줘"}],
        tools=[WEATHER_TOOL],
    )
    calls = tool_response.choices[0].message.tool_calls
    tool_text = f"{calls[0].function.name}({json.loads(calls[0].function.arguments)['city']})" if calls else "없음"

    print(f"{alias:12} {seconds:>5.1f}초 {answer.usage.completion_tokens:>5} {cost:>10.6f}  "
          f"{tool_text:15} {answer.choices[0].message.content[:60]}")
