"""02-3. OpenAI SDK로 LiteLLM Proxy 호출하기 — base_url만 바꾼다"""
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="http://localhost:4000",
    api_key=os.environ["LITELLM_MASTER_KEY"],
)

response = client.chat.completions.create(
    model="gpt-6.1-sol",
    messages=[{"role": "user",
               "content": "LiteLLM Proxy를 한 문장으로 소개해 주세요."}],
)
print(response.model, "|", response.choices[0].message.content)
