"""10-4. 시나리오 결과(통과·시간)와 Gateway DB의 키별 최종 비용을 합쳐 요약한다 (Gateway 서버에서 실행)

사용: python aggregate.py results_scenario.jsonl <compose 폴더> > summary.json
"""
import json
import statistics
import subprocess
import sys
from collections import defaultdict

rows = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
compose_dir = sys.argv[2]

sql = """select t.key_alias, count(*), sum(s.prompt_tokens), sum(s.completion_tokens),
 sum(coalesce((s.metadata->'usage_object'->>'cache_read_input_tokens')::int,0)), sum(s.spend)
 from "LiteLLM_SpendLogs" s join "LiteLLM_VerificationToken" t on t.token = s.api_key
 where t.key_alias like 's%-%' group by t.key_alias"""
out = subprocess.run(["docker", "compose", "-p", "litellm-prod", "exec", "-T", "db", "psql", "-U", "litellm", "-d", "litellm",
                      "-tA", "-F", "|", "-c", sql], cwd=compose_dir, capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout
db = {}
for line in out.strip().splitlines():
    alias, n, pt, ct, cache, spend = line.split("|")
    db[alias] = dict(requests=int(n), prompt=int(pt or 0), completion=int(ct or 0), cache=int(cache or 0), cost=float(spend or 0))

SHORT = {"A-cloud": "A-cloud", "A2-fast": "A2-fast", "B-local": "B-local"}
per = defaultdict(lambda: dict(runs=0, passed=0, seconds=[], cost=0.0, prompt=0, completion=0, cache=0,
                               escalations=0, local_seconds=0.0, tiers=defaultdict(int)))
detail = defaultdict(dict)
for r in rows:
    sc, rnd, task = r["scenario"], r["round"], r["task"]
    if sc in SHORT:
        aliases = [f"s{rnd}-{sc}-{task}"]
    elif sc == "C-local-first":
        aliases = [f"s{rnd}-C1-{task}", f"s{rnd}-C2-{task}"]
    else:
        aliases = [f"s{rnd}-D-{task}"]
    usage = [db.get(a, dict(requests=0, prompt=0, completion=0, cache=0, cost=0.0)) for a in aliases]
    p = per[sc]
    p["runs"] += 1
    p["passed"] += int(r["passed"])
    p["seconds"].append(r["seconds"])
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
        if r["alias"] == "local":
            p["local_seconds"] += r["seconds"]
    detail[sc][f"{task}#{rnd}"] = ("O" if r["passed"] else "X") + ("*" if r.get("escalated") else "")

summary = {}
for sc, p in per.items():
    summary[sc] = dict(runs=p["runs"], passed=p["passed"], success_rate=round(p["passed"] / p["runs"], 3),
                       median_seconds=statistics.median(p["seconds"]), total_seconds=round(sum(p["seconds"]), 1),
                       cost_usd=round(p["cost"], 4), cost_per_task_usd=round(p["cost"] / p["runs"], 5),
                       prompt_tokens=p["prompt"], completion_tokens=p["completion"], cache_read_tokens=p["cache"],
                       escalations=p["escalations"], local_gpu_seconds=round(p["local_seconds"], 1),
                       tiers=dict(p["tiers"]), detail=detail[sc])
print(json.dumps(summary, ensure_ascii=False, indent=1))
