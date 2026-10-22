"""02-2. LiteLLM SDK로 첫 모델 호출하기"""
from dotenv import load_dotenv
import litellm

load_dotenv()  # 현재 폴더의 .env에서 OPENAI_API_KEY를 읽는다

response = litellm.completion(
    model="openai/gpt-6-luna",
    messages=[{"role": "user",
               "content": "LiteLLM을 한 문장으로 설명해 주세요."}],
)

print("응답:", response.choices[0].message.content)
print("모델:", response.model)
print("종료 이유:", response.choices[0].finish_reason)
print("토큰:", response.usage.prompt_tokens, "+",
      response.usage.completion_tokens, "=", response.usage.total_tokens)
print("비용(USD):", litellm.completion_cost(completion_response=response))
