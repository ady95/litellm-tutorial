"""06-1~06-3. Mock 서버를 상대로 Gateway의 라우팅·재시도·Fallback·쿨다운을 관찰한다

사용: python experiments.py [pool|retry|fallback|timeout|cooldown|all]
"""
import os
import sys
import time
from collections import Counter

import httpx
from dotenv import load_dotenv

load_dotenv()
GATEWAY = os.environ.get("LITELLM_BASE_URL", "http://localhost:4000")
MOCK = os.environ.get("MOCK_STATS_URL", "http://localhost:8901")
HEADERS = {"Authorization": f"Bearer {os.environ['LITELLM_MASTER_KEY']}"}


def ask(alias):
    start = time.time()
    r = httpx.post(f"{GATEWAY}/v1/chat/completions", headers=HEADERS, timeout=120,
                   json={"model": alias, "messages": [{"role": "user", "content": "hi"}]})
    return r, time.time() - start


def mock_calls():
    return httpx.get(f"{MOCK}/stats").json()


def reset():
    httpx.post(f"{MOCK}/reset")


def show(alias, r, seconds):
    h = r.headers
    body = r.json()
    result = body["choices"][0]["message"]["content"] if r.status_code == 200 else body["error"]["message"][:90]
    print(f"  [{alias}] HTTP {r.status_code} {seconds:.2f}초 "
          f"retries={h.get('x-litellm-attempted-retries')} fallbacks={h.get('x-litellm-attempted-fallbacks')} :: {result}")


def pool():
    print("== 부하 분산: pool 별칭에 100번 요청 (가중치 3:1)")
    reset()
    for _ in range(100):
        ask("pool")
    print("  Mock이 받은 요청:", mock_calls())


def retry():
    print("== 재시도: 항상 429 / 항상 500")
    for alias in ("always-429", "always-500"):
        reset()
        r, s = ask(alias)
        show(alias, r, s)
        print("  Mock이 받은 요청:", mock_calls())


def fallback():
    print("== Fallback: primary(500) -> backup")
    reset()
    r, s = ask("primary")
    show("primary", r, s)
    print("  Mock이 받은 요청:", mock_calls())


def timeout():
    print("== 타임아웃: slow(응답 없음, timeout 3초) -> backup")
    reset()
    r, s = ask("slow")
    show("slow", r, s)
    print("  Mock이 받은 요청:", mock_calls())


def cooldown():
    print("== 쿨다운: mixed(고장 1 + 정상 1)에 20번 요청")
    reset()
    results = Counter()
    for i in range(20):
        r, s = ask("mixed")
        results[r.status_code] += 1
        if i < 3 or i == 19:
            show(f"mixed #{i + 1}", r, s)
    print("  응답 코드:", dict(results), " Mock이 받은 요청:", mock_calls())


STEPS = {"pool": pool, "retry": retry, "fallback": fallback, "timeout": timeout, "cooldown": cooldown}

if __name__ == "__main__":
    for name in (STEPS if sys.argv[1:] in ([], ["all"]) else sys.argv[1:]):
        STEPS[name]()
