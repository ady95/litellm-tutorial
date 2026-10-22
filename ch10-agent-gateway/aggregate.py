"""10-4. 시나리오 결과(통과·시간)와 Gateway DB의 키별 최종 비용을 합쳐 요약한다 (Gateway 서버에서 실행)

사용: python aggregate.py results_scenario.jsonl <compose 폴더> <compose 프로젝트 이름> > summary.json
      예) python aggregate.py results/results_scenario.jsonl ../ch09-security-operations litellm-prod > results/summary.json

- 키별 DB 집계(요청 수·토큰·비용)를 results/per_key_usage.json에 함께 남긴다. 키 값은 없고 별칭만 있다.
- DB 조회가 실패하거나, 실행한 키의 기록이 DB에 없으면 비용 0으로 채우지 않고 중단한다.
  기록이 없어도 되는 것은 에스컬레이션하지 않아 실행하지 않은 C2 키뿐이다.
- D(분류기) 시나리오의 시간에는 분류 호출 시간(classify_seconds)을 더한다. 분류는 로컬 모델이 하므로 GPU 시간에도 더한다.
"""
import json
import os
import statistics
import subprocess
import sys
from collections import defaultdict

if len(sys.argv) != 4:
    sys.exit(__doc__)
rows = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
compose_dir, project = sys.argv[2], sys.argv[3]

sql = """select t.key_alias, count(*), sum(s.prompt_tokens), sum(s.completion_tokens),
 sum(coalesce((s.metadata->'usage_object'->>'cache_read_input_tokens')::int,0)), sum(s.spend)
 from "LiteLLM_SpendLogs" s join "LiteLLM_VerificationToken" t on t.token = s.api_key
 where t.key_alias like 's%-%' group by t.key_alias order by t.key_alias"""
proc = subprocess.run(["docker", "compose", "-p", project, "exec", "-T", "db", "psql", "-U", "litellm", "-d", "litellm",
                       "-v", "ON_ERROR_STOP=1", "-tA", "-F", "|", "-c", sql],
                      cwd=compose_dir, capture_output=True, text=True, stdin=subprocess.DEVNULL)
if proc.returncode != 0:
    sys.exit(f"DB 조회 실패 (프로젝트 {project}, 폴더 {compose_dir}):\n{proc.stderr.strip()}")
db = {}
for line in proc.stdout.strip().splitlines():
    alias, n, pt, ct, cache, spend = line.split("|")
    db[alias] = dict(requests=int(n), prompt=int(pt or 0), completion=int(ct or 0), cache=int(cache or 0), cost=float(spend or 0))

SHORT = {"A-cloud": "A-cloud", "A2-fast": "A2-fast", "B-local": "B-local"}
EMPTY = dict(requests=0, prompt=0, completion=0, cache=0, cost=0.0)
per = defaultdict(lambda: dict(runs=0, passed=0, seconds=[], cost=0.0, prompt=0, completion=0, cache=0,
                               escalations=0, local_seconds=0.0, tiers=defaultdict(int)))
detail = defaultdict(dict)
missing = []
for r in rows:
    sc, rnd, task = r["scenario"], r["round"], r["task"]
    if sc in SHORT:
        aliases = [f"s{rnd}-{sc}-{task}"]
    elif sc == "C-local-first":
        aliases = [f"s{rnd}-C1-{task}"] + ([f"s{rnd}-C2-{task}"] if r.get("escalated") else [])
    else:
        aliases = [f"s{rnd}-D-{task}"]
    missing += [a for a in aliases if a not in db]
    usage = [db.get(a, EMPTY) for a in aliases]
    seconds = r["seconds"] + r.get("classify_seconds", 0)
    p = per[sc]
    p["runs"] += 1
    p["passed"] += int(r["passed"])
    p["seconds"].append(seconds)
    p["cost"] += sum(u["cost"] for u in usage)
    p["prompt"] += sum(u["prompt"] for u in usage)
    p["completion"] += sum(u["completion"] for u in usage)
    p["cache"] += sum(u["cache"] for u in usage)
    p["escalations"] += int(bool(r.get("escalated")))
    if sc == "B-local":
        p["local_seconds"] += r["seconds"]
    elif sc == "C-local-first":
        p["local_seconds"] += r.get("local_seconds", 0)
    elif sc == "D-classifier":
        p["tiers"][r.get("tier", "?")] += 1
        p["local_seconds"] += r.get("classify_seconds", 0)
        if r["alias"] == "local":
            p["local_seconds"] += r["seconds"]
    detail[sc][f"{task}#{rnd}"] = ("O" if r["passed"] else "X") + ("*" if r.get("escalated") else "")

if missing:
    sys.exit(f"실행했지만 DB에 기록이 없는 키 {len(missing)}개: {', '.join(missing[:10])} ... "
             "DB 기록이 끝났는지(수 초 지연) 확인하고 다시 실행하세요.")

with open(os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), "per_key_usage.json"), "w", encoding="utf-8") as f:
    json.dump(db, f, ensure_ascii=False, indent=1)

summary = {}
for sc, p in per.items():
    summary[sc] = dict(runs=p["runs"], passed=p["passed"], success_rate=round(p["passed"] / p["runs"], 3),
                       median_seconds=round(statistics.median(p["seconds"]), 2),
                       total_seconds=round(sum(p["seconds"]), 1),
                       cost_usd=round(p["cost"], 4), cost_per_task_usd=round(p["cost"] / p["runs"], 5),
                       prompt_tokens=p["prompt"], completion_tokens=p["completion"], cache_read_tokens=p["cache"],
                       escalations=p["escalations"], local_gpu_seconds=round(p["local_seconds"], 1),
                       tiers=dict(p["tiers"]), detail=detail[sc])
summary["_meta"] = dict(db_keys=len(db), db_requests=sum(u["requests"] for u in db.values()))
print(json.dumps(summary, ensure_ascii=False, indent=1))
