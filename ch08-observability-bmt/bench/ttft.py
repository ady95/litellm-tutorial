"""8장 2단계 보조: 스트리밍 응답에서 '첫 내용 토큰'까지의 시간(TTFT)을 직접 잰다

k6의 첫 바이트 시간은 서버가 헤더나 빈 청크를 먼저 보내면 TTFT보다 짧게 나온다.
여기서는 SSE를 한 줄씩 읽어 delta.content가 처음 비어 있지 않은 순간을 기록한다.
표준 라이브러리만 쓴다.

사용: python3 ttft.py <기본 URL> <모델> <동시 수> <요청 수> [키]
"""
import concurrent.futures
import json
import statistics
import sys
import time
import urllib.request

url, model, concurrency, total = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
key = sys.argv[5] if len(sys.argv) > 5 else ""
body = json.dumps({
    "model": model, "max_tokens": 128, "stream": True,
    "chat_template_kwargs": {"enable_thinking": False},
    "messages": [{"role": "user", "content": "AI Gateway가 필요한 이유를 자세히 설명하세요."}],
}).encode()
headers = {"Content-Type": "application/json"}
if key:
    headers["Authorization"] = f"Bearer {key}"


def one(_):
    start = time.time()
    first_byte = first_token = None
    req = urllib.request.Request(f"{url}/v1/chat/completions", data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=300) as resp:
        for raw in resp:
            first_byte = first_byte or time.time() - start
            line = raw.decode().strip()
            if not line.startswith("data:") or line == "data: [DONE]":
                continue
            chunk = json.loads(line[5:])
            choices = chunk.get("choices") or []
            if choices and (choices[0].get("delta") or {}).get("content"):
                first_token = first_token or time.time() - start
    return first_byte, first_token, time.time() - start


with concurrent.futures.ThreadPoolExecutor(concurrency) as pool:
    results = list(pool.map(one, range(total)))
fb, ft, tt = (sorted(x[i] * 1000 for x in results) for i in range(3))
p95 = lambda v: v[int(len(v) * 0.95) - 1]
print(json.dumps({"concurrency": concurrency, "n": total,
                  "first_byte_p50_ms": round(statistics.median(fb), 1),
                  "ttft_p50_ms": round(statistics.median(ft), 1), "ttft_p95_ms": round(p95(ft), 1),
                  "total_p50_ms": round(statistics.median(tt), 1)}))
