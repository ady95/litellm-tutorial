// 8장 2단계. 동시 사용자 수(VUs)를 고정하고 실제 추론 서버의 처리량·지연·TTFT를 잰다
// 환경변수: TARGET, MODEL, KEY, VUS, DURATION, STREAM(true/false), OUT
import http from "k6/http";
import { check } from "k6";
import { Counter } from "k6/metrics";

const outputTokens = new Counter("output_tokens");
const STREAM = __ENV.STREAM === "true";

export const options = {
  scenarios: {
    load: { executor: "constant-vus", vus: Number(__ENV.VUS || 1), duration: __ENV.DURATION || "40s" },
  },
  summaryTrendStats: ["avg", "med", "p(95)", "p(99)", "max"],
};

const headers = { "Content-Type": "application/json" };
if (__ENV.KEY) headers["Authorization"] = `Bearer ${__ENV.KEY}`;
const body = JSON.stringify({
  model: __ENV.MODEL,
  max_tokens: 128,
  stream: STREAM,
  chat_template_kwargs: { enable_thinking: false },
  messages: [{ role: "user", content: "AI Gateway가 필요한 이유를 자세히 설명하세요." }],
});

export default function () {
  const res = http.post(`${__ENV.TARGET}/v1/chat/completions`, body, { headers, timeout: "300s" });
  check(res, { "status 200": (r) => r.status === 200 });
  if (res.status === 200 && !STREAM) {
    outputTokens.add(res.json("usage.completion_tokens") || 0);
  }
}

export function handleSummary(data) {
  const m = data.metrics;
  const sec = data.state.testRunDurationMs / 1000;
  const out = {
    vus: Number(__ENV.VUS || 1),
    stream: STREAM,
    requests: m.http_reqs.values.count,
    rps: m.http_reqs.values.rate,
    failed_rate: m.http_req_failed.values.rate,
    latency_p50_ms: m.http_req_duration.values.med,
    latency_p95_ms: m.http_req_duration.values["p(95)"],
    ttfb_p50_ms: m.http_req_waiting.values.med,       // 스트리밍일 때 TTFT 근사
    ttfb_p95_ms: m.http_req_waiting.values["p(95)"],
    output_tok_per_s: m.output_tokens ? m.output_tokens.values.count / sec : null,
  };
  return { [__ENV.OUT || "/dev/stdout"]: JSON.stringify(out) + "\n" };
}
