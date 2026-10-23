"""03-1. 같은 요청을 세 제공자에 보내기"""
import time

from dotenv import load_dotenv
import litellm

load_dotenv()

MODELS = [
    "openai/gpt-6-luna",                    # OPENAI_API_KEY
    "anthropic/claude-sonnet-5-5",          # ANTHROPIC_API_KEY
    "openrouter/google/gemini-3.8-flash",   # OPENROUTER_API_KEY
]

messages = [
    {"role": "system", "content": "항상 한 문장으로 답합니다."},
    {"role": "user", "content": "LiteLLM이 무엇인가요?"},
]

for model in MODELS:
    start = time.time()
    try:
        response = litellm.completion(model=model, messages=messages)
    except Exception as e:   # 키가 없는 제공자는 오류만 보이고 다음으로
        print(f"[{model}] 실패: {type(e).__name__}")
        continue
    print(f"[{model}] {time.time() - start:.1f}초")
    print("  응답:", response.choices[0].message.content)
    usage = response.usage
    print("  토큰:", usage.prompt_tokens, "+", usage.completion_tokens)
