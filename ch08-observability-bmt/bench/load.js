// 8장. 일정한 요청률(RPS)로 OpenAI 호환 엔드포인트에 부하를 건다
// 환경변수: TARGET(기본 URL), MODEL, KEY(없으면 인증 헤더 생략), RATE, DURATION, MAX_TOKENS, OUT(결과 JSON)
import http from "k6/http";
import { check } from "k6";

const RATE = Number(__ENV.RATE || 50);

export const options = {
  discardResponseBodies: false,
  scenarios: {
    load: {
      executor: "constant-arrival-rate",
      rate: RATE,
      timeUnit: "1s",
      duration: __ENV.DURATION || "30s",
      preAllocatedVUs: Math.min(RATE * 2, 400),
      maxVUs: 1500,
    },
  },
  summaryTrendStats: ["avg", "min", "med", "p(90)", "p(95)", "p(99)", "max"],
};

const headers = { "Content-Type": "application/json" };
if (__ENV.KEY) headers["Authorization"] = `Bearer ${__ENV.KEY}`;
const body = JSON.stringify({
  model: __ENV.MODEL,
  max_tokens: Number(__ENV.MAX_TOKENS || 16),
  messages: [{ role: "user", content: "한 단어로 답하세요: 하늘색은?" }],
});

export default function () {
  const res = http.post(`${__ENV.TARGET}/v1/chat/completions`, body, { headers, timeout: "120s" });
  check(res, { "status 200": (r) => r.status === 200 });
}

export function handleSummary(data) {
  const m = data.metrics;
  const d = m.http_req_duration.values;
  const out = {
    target_rate: RATE,
    achieved_rps: m.http_reqs.values.rate,
    requests: m.http_reqs.values.count,
    failed_rate: m.http_req_failed.values.rate,
    dropped: m.dropped_iterations ? m.dropped_iterations.values.count : 0,
    p50_ms: d.med, p90_ms: d["p(90)"], p95_ms: d["p(95)"], p99_ms: d["p(99)"], max_ms: d.max,
  };
  return { [__ENV.OUT || "/dev/stdout"]: JSON.stringify(out) + "\n" };
}
