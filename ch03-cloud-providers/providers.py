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
    response = litellm.completion(model=model, messages=messages)
    print(f"[{model}] {time.time() - start:.1f}초")
    print("  응답:", response.choices[0].message.content)
    print("  토큰:", response.usage.prompt_tokens, "+", response.usage.completion_tokens)
