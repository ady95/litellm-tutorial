"""05-2, 05-3. SDK로 로컬 추론 서버 호출하기 (Ollama, vLLM)"""
import os
import time

from dotenv import load_dotenv
import litellm

load_dotenv()

TARGETS = [
    # Ollama: ollama_chat/ 접두사 + Ollama 주소
    dict(model="ollama_chat/qwen3.5:2b", api_base=os.environ["OLLAMA_API_BASE"]),
    # vLLM: hosted_vllm/ 접두사 + OpenAI 호환 주소(/v1까지)
    dict(model="hosted_vllm/qwen3.5-9b", api_base=os.environ["VLLM_API_BASE"]),
]

for target in TARGETS:
    start = time.time()
    response = litellm.completion(
        messages=[{"role": "user", "content": "LiteLLM을 한 문장으로 설명하세요."}],
        reasoning_effort="none",   # Qwen3.5의 생각 모드를 끈다
        **target,
    )
    print(f"[{target['model']}] {time.time() - start:.1f}초, 출력 {response.usage.completion_tokens}토큰")
    print("  ", response.choices[0].message.content)
