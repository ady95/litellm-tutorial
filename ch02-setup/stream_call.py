"""02-2. 스트리밍으로 받기"""
from dotenv import load_dotenv
import litellm

load_dotenv()

stream = litellm.completion(
    model="openai/gpt-6-luna",
    messages=[{"role": "user",
               "content": "숫자 1부터 5까지 쉼표로 이어서 써 주세요."}],
    stream=True,
)

chunks = 0
for chunk in stream:
    chunks += 1
    text = chunk.choices[0].delta.content
    if text:
        print(text, end="", flush=True)
print(f"\n(청크 {chunks}개)")
