# 8장. AI Gateway 모니터링과 성능 평가하기

검증 환경: LiteLLM Proxy 1.106.1, Bifrost v2.3.2, vLLM 0.31.0 (RTX 3090), k6 1.3.0, Prometheus v3.15.0, Grafana 13.2.4

## monitoring/ — Prometheus + Grafana

```bash
cd monitoring
# 내용은 마스터 키다. Prometheus 컨테이너 사용자(nobody, 65534)만 읽게 한다
umask 077 && printf '%s' "$LITELLM_MASTER_KEY" > litellm_metrics_key
sudo chown 65534:65534 litellm_metrics_key && sudo chmod 400 litellm_metrics_key
echo "GRAFANA_ADMIN_PASSWORD=$(openssl rand -hex 12)" > .env
docker compose up -d     # Prometheus :9095, Grafana :3005
```

LiteLLM `config.yaml`의 `litellm_settings`에 `callbacks: ["prometheus"]`가 있어야 합니다. 대시보드는 `grafana/dashboards/litellm-gateway.json`에서 자동 등록됩니다.

## bench/ — LiteLLM vs Bifrost BMT

| 파일 | 내용 |
|---|---|
| `load.js` | 1단계: 일정 RPS 부하 (k6 constant-arrival-rate) |
| `load_vus.js` | 2단계: 동시 사용자 고정, 처리량·지연 |
| `ttft.py` | 2단계: SSE를 직접 읽어 첫 내용 토큰까지 시간 측정 (k6 첫 바이트 ≠ TTFT) |
| `litellm-bench.yaml` | LiteLLM BMT 설정 (DB·로그 없음) |
| `bifrost-config.json` | Bifrost BMT 설정 (`MOCK_HOST`, `GPU_HOST`를 실제 주소로) |
| `run_phase1.sh` | 1단계 실행 (부하 서버에서) |
| `summarize_phase1.py`, `summarize_phase2.py` | 결과 요약 |

Mock 서버는 6장 `mock_llm.py`를 부하 서버에서 실행합니다(`uvicorn mock_llm:app --port 8901 --workers 4`). k6 컨테이너는 일반 사용자로 실행되므로 결과 폴더에 쓰기 권한이 필요합니다.

## results/ — 원자료

| 파일 | 내용 |
|---|---|
| `phase1.jsonl` | 1단계 60회 측정 (직접·LiteLLM 워커1·워커4·Bifrost × 5개 RPS × 3회) |
| `phase1-cpu.jsonl` | 1단계 CPU·메모리 (docker stats) |
| `phase2-k6.jsonl` | 2단계 k6 (직접·LiteLLM·Bifrost × VUs 1/8/32 × 스트리밍 여부 × 2회) |
| `phase2-ttft.jsonl` | 2단계 TTFT 직접 측정 |

측정 환경: Gateway = Intel N100 4코어/16GB, 부하·Mock = i7-5820K, 백엔드 = RTX 3090 + Qwen3.5-9B(BF16). 상세 조건과 해석은 책 08-3~08-5를 참고하세요.
