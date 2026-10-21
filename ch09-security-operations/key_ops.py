"""09-2, 09-3. 키 차단·삭제·재발급과 Enterprise 기능 경계를 관리 포트에서 시험한다

관리 포트(127.0.0.1:8444)는 Gateway 서버 안에서만 열려 있으므로 서버에서 실행한다.
사용: python key_ops.py [revoke|regenerate|enterprise]
"""
import os
import sys

import httpx
from dotenv import load_dotenv

load_dotenv()
ADMIN = os.environ.get("LITELLM_ADMIN_URL", "http://127.0.0.1:8444")
MASTER = {"Authorization": f"Bearer {os.environ['LITELLM_MASTER_KEY']}"}


def admin(path, payload=None, method="POST"):
    r = httpx.request(method, f"{ADMIN}{path}", headers=MASTER, json=payload, timeout=30)
    return r.status_code, (r.json() if "json" in r.headers.get("content-type", "") else r.text)


def chat(key):
    r = httpx.post(f"{ADMIN}/v1/chat/completions", headers={"Authorization": f"Bearer {key}"}, timeout=30,
                   json={"model": "mock", "messages": [{"role": "user", "content": "hi"}]})
    return r.status_code, ("OK" if r.status_code == 200 else str(r.json().get("error", {}).get("message"))[:110])


def short(body):
    return str(body)[:140]


def revoke():
    print("== 차단·해제·삭제")
    key = admin("/key/generate", {"key_alias": "ops-1", "models": ["mock"]})[1]["key"]
    print("  발급 직후      ", chat(key))
    print("  /key/block    ", admin("/key/block", {"key": key})[0], "→", chat(key))
    print("  /key/unblock  ", admin("/key/unblock", {"key": key})[0], "→", chat(key))
    print("  /key/delete   ", admin("/key/delete", {"keys": [key]})[0], "→", chat(key))


def regenerate():
    print("== 키 재발급")
    key = admin("/key/generate", {"key_alias": "ops-2", "models": ["mock"]})[1]["key"]
    code, body = admin(f"/key/{key}/regenerate", {})
    print(f"  /key/{{key}}/regenerate: HTTP {code} :: {short(body)}")
    if code == 200:
        new = body["key"]
        print("  이전 키 →", chat(key), " / 새 키 →", chat(new))


def enterprise():
    print("== 기능별 경계 (OSS 이미지)")
    trials = [
        ("키에 허용 IP 지정", "/key/generate", {"key_alias": "ip", "models": ["mock"], "allowed_ips": ["10.0.0.1"]}),
        ("키에 가드레일 지정", "/key/generate", {"key_alias": "gr", "models": ["mock"], "guardrails": ["pii"]}),
        ("팀 멤버별 예산", "/team/new", {"team_alias": "t-member", "team_member_budget": 1.0}),
        ("키 동시 요청 제한", "/key/generate", {"key_alias": "par", "models": ["mock"], "max_parallel_requests": 2}),
        ("키 메타데이터 태그", "/key/generate", {"key_alias": "tag", "models": ["mock"], "tags": ["prod"]}),
    ]
    for name, path, payload in trials:
        code, body = admin(path, payload)
        print(f"  {name:14} HTTP {code} :: {short(body)}")
    for name, path in [("감사 로그 조회", "/audit"), ("SSO 설정 조회", "/sso/debug/login")]:
        code, body = admin(path, method="GET")
        print(f"  {name:14} HTTP {code} :: {short(body)}")


STEPS = {"revoke": revoke, "regenerate": regenerate, "enterprise": enterprise}
if __name__ == "__main__":
    for name in sys.argv[1:] or STEPS:
        STEPS[name]()
