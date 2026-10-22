"""07장. 가상 키·팀·예산·속도 제한을 차례로 시험한다

사용: python keys_lab.py [models|budget|rpm|team|admin|all]
"""
import os
import sys
import time

import httpx
from dotenv import load_dotenv

load_dotenv()
GATEWAY = os.environ.get("LITELLM_BASE_URL", "http://localhost:4000")
MASTER = {"Authorization": f"Bearer {os.environ['LITELLM_MASTER_KEY']}"}


def admin(path, payload=None):
    """마스터 키로 관리 API를 부른다."""
    if payload is None:
        return httpx.get(f"{GATEWAY}{path}", headers=MASTER, timeout=30).json()
    return httpx.post(f"{GATEWAY}{path}", headers=MASTER, json=payload, timeout=30).json()


def chat(key, model):
    r = httpx.post(f"{GATEWAY}/v1/chat/completions", timeout=60,
                   headers={"Authorization": f"Bearer {key}"},
                   json={"model": model, "max_tokens": 20,
                         "messages": [{"role": "user", "content": "한 단어로: 하늘색은?"}]})
    message = "OK" if r.status_code == 200 else r.json()["error"]["message"]
    return r.status_code, message


def spend(key):
    return admin(f"/key/info?key={key}")["info"]["spend"]


def models():
    print("== 허용 모델 제한: mock만 허용한 키")
    key = admin("/key/generate", {"key_alias": "only-mock", "models": ["mock"]})["key"]
    print(f"  발급된 키: {key[:7]}...{key[-4:]}")
    for model in ("mock", "fast"):
        code, message = chat(key, model)
        print(f"  [{model}] HTTP {code} :: {message[:150]}")


def budget():
    print("== 예산: max_budget 0.03달러, 호출당 0.01달러")
    key = admin("/key/generate", {"key_alias": "budget-3c", "models": ["mock"],
                              "max_budget": 0.03})["key"]
    for i in range(1, 8):
        code, message = chat(key, "mock")
        print(f"  {i}번째 HTTP {code} spend={spend(key):.4f} :: {message[:110]}")
        time.sleep(1)


def rpm():
    print("== 속도 제한: rpm_limit 2")
    key = admin("/key/generate", {"key_alias": "rpm-2", "models": ["mock"], "rpm_limit": 2})["key"]
    for i in range(1, 5):
        code, message = chat(key, "mock")
        print(f"  {i}번째 HTTP {code} :: {message[:110]}")


def team():
    print("== 팀 예산: 팀 max_budget 0.02달러, 팀 소속 키 2개")
    team_id = admin("/team/new", {"team_alias": "research", "models": ["mock", "local"], "max_budget": 0.02})["team_id"]
    key_a = admin("/key/generate", {"key_alias": "research-a", "team_id": team_id})["key"]
    key_b = admin("/key/generate", {"key_alias": "research-b", "team_id": team_id})["key"]
    for i, key in enumerate([key_a, key_b, key_a, key_b, key_a], 1):
        code, message = chat(key, "mock")
        team_spend = admin(f"/team/info?team_id={team_id}")["team_info"]["spend"]
        print(f"  {i}번째 ({'A' if key == key_a else 'B'}) HTTP {code} team_spend={team_spend:.4f} :: {message[:90]}")
        time.sleep(1)
    code, message = chat(key_a, "fast")
    print(f"  팀에 없는 모델(fast) HTTP {code} :: {message[:110]}")


def admin_rights():
    print("== 권한: 가상 키로 관리 API 호출, 틀린 키")
    key = admin("/key/generate", {"key_alias": "plain", "models": ["mock"]})["key"]
    r = httpx.post(f"{GATEWAY}/key/generate", headers={"Authorization": f"Bearer {key}"}, json={}, timeout=30)
    print(f"  가상 키로 /key/generate: HTTP {r.status_code} :: {r.text[:120]}")
    code, message = chat("sk-not-a-real-key", "mock")
    print(f"  틀린 키: HTTP {code} :: {message[:120]}")


STEPS = {"models": models, "budget": budget, "rpm": rpm, "team": team, "admin": admin_rights}

if __name__ == "__main__":
    for name in (STEPS if sys.argv[1:] in ([], ["all"]) else sys.argv[1:]):
        STEPS[name]()
