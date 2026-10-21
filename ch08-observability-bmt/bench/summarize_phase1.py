import json
import statistics
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
rows = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
groups = defaultdict(list)
for r in rows:
    groups[(r["target"], r["target_rate"])].append(r)

direct_p50 = {rate: statistics.median(r["p50_ms"] for r in groups[("direct", rate)]) for _, rate in groups if ("direct", rate) in groups}
print(f"{'대상':11} {'목표':>5} {'n':>2} {'달성RPS(중앙)':>12} {'p50 ms':>18} {'p95 ms':>18} {'p99 ms':>18} {'+p50 오버헤드':>12} {'미전송':>7} {'실패':>5}")
for (target, rate), rs in sorted(groups.items(), key=lambda x: (["direct", "litellm-1w", "litellm-4w", "bifrost"].index(x[0][0]), x[0][1])):
    def med_range(k):
        v = [r[k] for r in rs]
        return f"{statistics.median(v):8.1f} ({min(v):.1f}~{max(v):.1f})"
    over = statistics.median(r["p50_ms"] for r in rs) - direct_p50.get(rate, 0)
    print(f"{target:11} {rate:>5} {len(rs):>2} {statistics.median(r['achieved_rps'] for r in rs):>12.1f} "
          f"{med_range('p50_ms'):>18} {med_range('p95_ms'):>18} {med_range('p99_ms'):>18} {over:>12.1f} "
          f"{int(statistics.median(r['dropped'] for r in rs)):>7} {max(r['failed_rate'] for r in rs):>5.2f}")
