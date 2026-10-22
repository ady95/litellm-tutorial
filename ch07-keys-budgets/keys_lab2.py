"""07장 심화. 사용량 기록 시점, 동시 요청, 재시작, 만료, TPM, 실제 모델 비용

사용: python keys_lab2.py [flush|burst|restart|expiry|tpm|real]
restart는 docker-compose.yaml이 있는 폴더에서 실행한다 (다른 폴더면 COMPOSE_DIR 환경변수로 지정)
"""
import concurrent.futures
import os
import subprocess
import sys
import time

from keys_lab import admin, chat, spend

COMPOSE_DIR = os.environ.get("COMPOSE_DIR", os.path.dirname(os.path.abspath(__file__)))


def flush():
    print("== 사용 금액이 DB에 기록되기까지")
    key = admin("/key/generate", {"key_alias": "flush", "models": ["mock"]})["key"]
    chat(key, "mock")
    start = time.time()
    while spend(key) == 0 and time.time() - start < 180:
        time.sleep(2)
    print(f"  /key/info spend={spend(key):.4f} — 요청 후 약 {time.time() - start:.0f}초 뒤 반영")


def burst():
    print("== 동시 요청 10개, max_budget 0.03 (호출당 0.01)")
    key = admin("/key/generate", {"key_alias": "burst", "models": ["mock"], "max_budget": 0.03})["key"]
    with concurrent.futures.ThreadPoolExecutor(10) as pool:
        codes = list(pool.map(lambda _: chat(key, "mock")[0], range(10)))
    print(f"  성공 {codes.count(200)}개, 차단 {len(codes) - codes.count(200)}개 → {codes}")


def compose(*args):
    """이 폴더(또는 COMPOSE_DIR)의 Compose 프로젝트에 명령을 보낸다. 실패하면 멈춘다."""
    r = subprocess.run(["docker", "compose", *args], cwd=COMPOSE_DIR, capture_output=True, text=True,
                       stdin=subprocess.DEVNULL)
    if r.returncode != 0:
        sys.exit(f"docker compose {' '.join(args)} 실패: {r.stderr.strip()}")
    return r.stdout.strip()


def started_at():
    container = compose("ps", "-q", "litellm")
    r = subprocess.run(["docker", "inspect", "-f", "{{.State.StartedAt}}", container], capture_output=True, text=True)
    return r.stdout.strip()


def restart():
    print("== 예산 0.03 키로 2번 호출 직후 Proxy 재시작, 이후 호출")
    key = admin("/key/generate", {"key_alias": "restart", "models": ["mock"], "max_budget": 0.03})["key"]
    for _ in range(2):
        chat(key, "mock")
    before = started_at()
    compose("restart", "litellm")
    after = started_at()
    if after == before:
        sys.exit("Proxy 컨테이너가 재시작되지 않았습니다.")
    print(f"  컨테이너 시작 시각 {before} → {after}")
    deadline = time.time() + 120
    while True:
        try:
            if admin("/health/liveliness") == "I'm alive!":
                break
        except Exception:
            pass
        if time.time() > deadline:
            sys.exit("재시작 후 120초 안에 Proxy가 응답하지 않았습니다.")
        time.sleep(1)
    for i in range(1, 5):
        code, message = chat(key, "mock")
        print(f"  재시작 후 {i}번째 HTTP {code} :: {message[:100]}")


def expiry():
    print("== duration 20s 키")
    key = admin("/key/generate", {"key_alias": "short", "models": ["mock"], "duration": "20s"})["key"]
    print("  발급 직후:", chat(key, "mock")[0])
    time.sleep(25)
    code, message = chat(key, "mock")
    print(f"  25초 뒤: HTTP {code} :: {message[:120]}")


def tpm():
    print("== tpm_limit 20 (호출당 15토큰)")
    key = admin("/key/generate", {"key_alias": "tpm-20", "models": ["mock"], "tpm_limit": 20})["key"]
    for i in range(1, 4):
        code, message = chat(key, "mock")
        print(f"  {i}번째 HTTP {code} :: {message[:110]}")


def real():
    print("== 실제 모델 비용 기록")
    key = admin("/key/generate", {"key_alias": "real", "models": ["local", "fast", "smart"]})["key"]
    for model in ("local", "fast", "smart"):
        print(f"  [{model}] HTTP {chat(key, model)[0]}")
    start = time.time()
    while spend(key) == 0 and time.time() - start < 180:
        time.sleep(2)
    logs = admin(f"/spend/logs?api_key={key}")
    for row in sorted(logs, key=lambda r: r["startTime"]):
        print(f"  {row['model_group']:6} {row['model']:28} 토큰 {row['prompt_tokens']}+{row['completion_tokens']} 비용 ${row['spend']:.6f}")
    print(f"  키 누적 spend=${spend(key):.6f}")


STEPS = {"flush": flush, "burst": burst, "restart": restart, "expiry": expiry, "tpm": tpm, "real": real}

if __name__ == "__main__":
    for name in sys.argv[1:] or STEPS:
        STEPS[name]()
