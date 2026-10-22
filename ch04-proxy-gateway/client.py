"""04-3. 기존 OpenAI SDK 코드를 Gateway로 돌리기 — base_url과 키, 모델 별칭만 바꾼다"""
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.environ.get("LITELLM_BASE_URL", "http://localhost:4000"),
    api_key=os.environ["LITELLM_MASTER_KEY"],
)

print("사용 가능한 모델:", [m.id for m in client.models.list().data])

for model in ["fast", "smart", "gemini", "openrouter/openai/gpt-6.1-sol"]:
    raw = client.chat.completions.with_raw_response.create(
        model=model,
        messages=[{"role": "user", "content": "한 단어로: 맑은 하늘의 색은?"}],
    )
    response = raw.parse()
    cost = float(raw.headers["x-litellm-response-cost"])
    overhead = float(raw.headers["x-litellm-overhead-duration-ms"])
    print(f"{model:30} {response.choices[0].message.content:8}"
          f" 비용=${cost:.6f} 오버헤드={overhead:.1f}ms")
