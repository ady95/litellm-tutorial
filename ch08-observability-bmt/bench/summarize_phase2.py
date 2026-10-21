import json
import statistics
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
rows = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
g = defaultdict(list)
for r in rows:
    g[(r["stream"], r["vus"], r["target"])].append(r)
order = ["direct", "litellm", "bifrost"]
for stream in (False, True):
    print("== stream" if stream else "== non-stream")
    if stream:
        print(f"{'VUs':>3} {'대상':8} {'n':>2} {'RPS':>6} {'TTFT p50':>10} {'TTFT p95':>10} {'전체 p50':>10} {'실패':>5}")
    else:
        print(f"{'VUs':>3} {'대상':8} {'n':>2} {'RPS':>6} {'출력 tok/s':>16} {'p50 ms':>10} {'p95 ms':>10} {'실패':>5}")
    for vus in (1, 8, 32):
        for t in order:
            rs = g[(stream, vus, t)]
            if not rs:
                continue
            m = lambda k: statistics.median(r[k] for r in rs)
            if stream:
                print(f"{vus:>3} {t:8} {len(rs):>2} {m('rps'):>6.2f} {m('ttfb_p50_ms'):>10.1f} {m('ttfb_p95_ms'):>10.1f} {m('latency_p50_ms'):>10.1f} {max(r['failed_rate'] for r in rs):>5.2f}")
            else:
                tok = [r["output_tok_per_s"] for r in rs]
                print(f"{vus:>3} {t:8} {len(rs):>2} {m('rps'):>6.2f} {statistics.median(tok):>8.1f} ({min(tok):.0f}~{max(tok):.0f}) {m('latency_p50_ms'):>10.1f} {m('latency_p95_ms'):>10.1f} {max(r['failed_rate'] for r in rs):>5.2f}")
