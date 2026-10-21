"""10장. 코딩 에이전트 × Gateway 별칭 × 과제를 실행하고 채점·비용을 기록한다 (Gateway 서버에서 실행)

사용:
  python bench_agents.py matrix  <결과.jsonl> [과제]          # 에이전트 3종 × 별칭 4종
  python bench_agents.py scenario <결과.jsonl> <에이전트> [회차]  # 시나리오 A~D × 과제 5개

환경변수: GATEWAY_HOST, LITELLM_MASTER_KEY, LITELLM_ADMIN_URL(기본 http://127.0.0.1:8444)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

import httpx

HERE = os.path.dirname(os.path.abspath(__file__))
TASKS = os.path.join(HERE, "tasks")
ADMIN = os.environ.get("LITELLM_ADMIN_URL", "http://127.0.0.1:8444")
MASTER = {"Authorization": f"Bearer {os.environ['LITELLM_MASTER_KEY']}"}
AGENT_TIMEOUT = 600

TIER_TO_ALIAS = {"SIMPLE": "local", "MEDIUM": "fast", "COMPLEX": "smart", "REASONING": "smart"}
RUBRIC = """다음 코딩 작업 지시의 난이도를 하나로 분류한다.
SIMPLE: 함수 하나를 설명대로 구현, 명백한 한 줄 수정
MEDIUM: 여러 조건이 있는 버그 수정, 기존 클래스에 기능 추가
COMPLEX: 입력 파싱·여러 규칙 검증처럼 경우의 수가 많고 정확한 출력 형식을 요구하는 작업
REASONING: 알고리즘 설계, 증명이 필요한 작업"""


def new_key(alias):
    r = httpx.post(f"{ADMIN}/key/generate", headers=MASTER, timeout=30,
                   json={"key_alias": alias, "models": ["local", "fast", "smart", "gemini"]})
    return r.json()["key"]


def usage(key):
    time.sleep(6)  # 사용 기록이 DB에 반영되기를 기다린다 (07-3)
    rows = httpx.get(f"{ADMIN}/spend/logs", params={"api_key": key}, headers=MASTER, timeout=30).json()
    return {
        "requests": len(rows),
        "prompt_tokens": sum(r.get("prompt_tokens") or 0 for r in rows),
        "completion_tokens": sum(r.get("completion_tokens") or 0 for r in rows),
        "cost_usd": round(sum(r.get("spend") or 0 for r in rows), 6),
        "models": sorted({r.get("model_group") or "" for r in rows}),
    }


def grade(work, task):
    shutil.copy(os.path.join(TASKS, task, "hidden_test.py"), os.path.join(work, "test_hidden_grading.py"))
    r = subprocess.run(["docker", "run", "--rm", "-v", f"{work}:/work", "-w", "/work", "--entrypoint", "python3",
                        "litellm-book-agents:1", "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_hidden_grading.py"],
                       capture_output=True, text=True)
    tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr.strip()[-200:]
    return r.returncode == 0, tail


def run_once(agent, alias, task, label):
    work = tempfile.mkdtemp(prefix=f"{task}-{agent}-{alias}-")
    shutil.copytree(os.path.join(TASKS, task, "start"), work, dirs_exist_ok=True)
    prompt = open(os.path.join(TASKS, task, "prompt.txt"), encoding="utf-8").read().strip()
    key = new_key(label)
    env = dict(os.environ, LITELLM_API_KEY=key)
    start = time.time()
    try:
        p = subprocess.run([os.path.join(HERE, "agent", "run_agent.sh"), agent, alias, work, prompt],
                           env=env, capture_output=True, text=True, timeout=AGENT_TIMEOUT)
        exit_code, log = p.returncode, (p.stdout + p.stderr)[-600:]
    except subprocess.TimeoutExpired as e:
        exit_code, log = "timeout", str(e.stdout or "")[-600:]
        subprocess.run("docker ps -q --filter ancestor=litellm-book-agents:1 | xargs -r docker kill", shell=True)
    seconds = round(time.time() - start, 1)
    passed, test_tail = grade(work, task)
    return dict(agent=agent, alias=alias, task=task, passed=passed, seconds=seconds, exit=exit_code,
                test=test_tail, **usage(key), log_tail=log.replace(key, "sk-***")[-300:])


def classify(task):
    prompt = open(os.path.join(TASKS, task, "prompt.txt"), encoding="utf-8").read()
    schema = {"type": "json_schema", "json_schema": {"name": "tier", "strict": True, "schema": {
        "type": "object", "properties": {"tier": {"type": "string", "enum": list(TIER_TO_ALIAS)}},
        "required": ["tier"], "additionalProperties": False}}}
    start = time.time()
    r = httpx.post(f"{ADMIN}/v1/chat/completions", headers=MASTER, timeout=60, json={
        "model": "local", "max_tokens": 50, "response_format": schema,
        "messages": [{"role": "system", "content": RUBRIC}, {"role": "user", "content": prompt}]})
    tier = json.loads(r.json()["choices"][0]["message"]["content"])["tier"]
    return tier, round(time.time() - start, 2)


def write(out, row):
    with open(out, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in row.items() if k != "log_tail"}, ensure_ascii=False), flush=True)


def matrix(out, task="t1-bugfix"):
    for agent in ("claude", "codex", "opencode"):
        for alias in ("local", "fast", "smart", "gemini"):
            write(out, run_once(agent, alias, task, f"m-{agent}-{alias}") | {"mode": "matrix"})


def scenario(out, agent, rnd=1):
    tasks = sorted(os.listdir(TASKS))
    for task in tasks:
        # A: 클라우드 전용 (smart), A2: 저가 클라우드 (fast), B: 로컬 전용
        for name, alias in (("A-cloud", "smart"), ("A2-fast", "fast"), ("B-local", "local")):
            write(out, run_once(agent, alias, task, f"s{rnd}-{name}-{task}") | {"mode": "scenario", "scenario": name, "round": rnd})
        # C: 로컬 먼저, 숨은 테스트 실패 시 클라우드(smart)로 다시
        first = run_once(agent, "local", task, f"s{rnd}-C1-{task}")
        row = first | {"mode": "scenario", "scenario": "C-local-first", "round": rnd, "escalated": False}
        if not first["passed"]:
            second = run_once(agent, "smart", task, f"s{rnd}-C2-{task}")
            row = second | {"mode": "scenario", "scenario": "C-local-first", "round": rnd, "escalated": True,
                            "seconds": first["seconds"] + second["seconds"],
                            "cost_usd": round(first["cost_usd"] + second["cost_usd"], 6),
                            "prompt_tokens": first["prompt_tokens"] + second["prompt_tokens"],
                            "completion_tokens": first["completion_tokens"] + second["completion_tokens"],
                            "local_seconds": first["seconds"]}
        else:
            row["local_seconds"] = first["seconds"]
        write(out, row)
        # D: 로컬 분류기가 고른 별칭으로 한 번
        tier, cls_sec = classify(task)
        alias = TIER_TO_ALIAS[tier]
        write(out, run_once(agent, alias, task, f"s{rnd}-D-{task}") | {"mode": "scenario", "scenario": "D-classifier",
                                                                        "round": rnd, "tier": tier, "classify_seconds": cls_sec})


if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    if mode == "matrix":
        matrix(out, *(sys.argv[3:4]))
    else:
        scenario(out, sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 1)
