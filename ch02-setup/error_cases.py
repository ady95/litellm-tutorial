"""02-4. 자주 만나는 오류를 일부러 재현해 보기"""
import os
import time

import litellm

litellm.suppress_debug_info = True
messages = [{"role": "user", "content": "hi"}]

cases = [
    ("틀린 API 키", dict(model="openai/gpt-6-luna", api_key="sk-wrong-key-for-test")),
    ("닫힌 포트", dict(model="openai/gpt-6-luna", api_key="x", api_base="http://127.0.0.1:59999/v1")),
    ("없는 호스트", dict(model="openai/gpt-6-luna", api_key="x", api_base="http://no-such-host.invalid/v1")),
    ("응답 없는 주소 + 5초 타임아웃", dict(model="openai/gpt-6-luna", api_key="x",
                                   api_base="http://10.255.255.1/v1", timeout=5)),
    ("제공자 접두사 없는 모르는 모델", dict(model="gpt-6-lunaa", api_key="x")),
]

for name, kwargs in cases:
    start = time.time()
    try:
        litellm.completion(messages=messages, **kwargs)
        print(f"[{name}] 성공")
    except Exception as e:
        status = getattr(e, "status_code", None)
        print(f"[{name}] {type(e).__name__} (status={status}, {time.time() - start:.1f}s)")
        print(f"    {str(e)[:150]}")

# 키가 아예 없는 경우: 환경변수를 잠시 지운다
saved = os.environ.pop("OPENAI_API_KEY", None)
try:
    litellm.completion(model="openai/gpt-6-luna", messages=messages)
except Exception as e:
    print(f"[키 없음] {type(e).__name__} (status={getattr(e, 'status_code', None)})")
    print(f"    {str(e)[:150]}")
finally:
    if saved is not None:
        os.environ["OPENAI_API_KEY"] = saved
