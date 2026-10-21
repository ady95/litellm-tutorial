"""06-5. 일정 간격으로 local 별칭을 호출하며 어느 모델이 답했는지 기록한다

사용: python failover_watch.py [총 초=300] [간격 초=5]
"""
import os
import sys
import time

import httpx
from dotenv import load_dotenv

load_dotenv()
GATEWAY = os.environ.get("LITELLM_BASE_URL", "http://localhost:4000")
HEADERS = {"Authorization": f"Bearer {os.environ['LITELLM_MASTER_KEY']}"}
duration = int(sys.argv[1]) if len(sys.argv) > 1 else 300
interval = int(sys.argv[2]) if len(sys.argv) > 2 else 5

info = httpx.get(f"{GATEWAY}/v1/model/info", headers=HEADERS).json()["data"]
names = {m["model_info"]["id"]: m["model_name"] for m in info}

begin = time.time()
while time.time() - begin < duration:
    start = time.time()
    try:
        r = httpx.post(f"{GATEWAY}/v1/chat/completions", headers=HEADERS, timeout=60,
                       json={"model": "local", "max_tokens": 20,
                             "messages": [{"role": "user", "content": "한 단어로: 하늘색은?"}]})
        served = names.get(r.headers.get("x-litellm-model-id"), "-")
        status = f"HTTP {r.status_code} 응답={served:5} fallbacks={r.headers.get('x-litellm-attempted-fallbacks')}"
    except httpx.HTTPError as e:
        status = f"클라이언트 오류 {type(e).__name__}"
    print(f"{start - begin:6.0f}s  {status}  {time.time() - start:5.2f}초", flush=True)
    time.sleep(max(0.0, interval - (time.time() - start)))
