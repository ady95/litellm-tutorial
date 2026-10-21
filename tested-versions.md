# 검증 버전표

책의 예제는 아래 버전에서 실행해 확인했습니다 (2026-10-21 ~ 2026-10-22).

## Gateway

| 소프트웨어 | 버전 | 비고 |
|---|---|---|
| LiteLLM (PyPI) | 1.106.1 | 1.82.7·1.82.8 사용 금지. Tool Calling은 `litellm[mcp]`로 설치 (#46045) |
| LiteLLM Proxy Docker 이미지 | `docker.litellm.ai/berriai/litellm:v1.106.1` | index digest `sha256:1acf80698f7eb47021b0bf5aed01ba9e80098cf74cdb3e588515bdd48a129fa6`, cosign 서명 확인 |
| openai (Python SDK) | 2.54.0 | litellm 의존성 |
| mcp | 2.3.0 | `litellm[mcp]` |
| Bifrost | v2.3.2 (`maximhq/bifrost`) | 8장 BMT |

## 로컬 추론

| 소프트웨어 | 버전 | 비고 |
|---|---|---|
| Ollama | 0.34.0 | Docker 이미지, `qwen3.5:0.8b/2b/4b/9b` |
| vLLM | 0.31.0 (`vllm/vllm-openai:v0.31.0`) | Qwen/Qwen3.5-9B BF16, RTX 3090 24GB |
| NVIDIA 드라이버 / CUDA | 580.178.04 / 13.0 | |

## 운영·관측

| 소프트웨어 | 버전 | 비고 |
|---|---|---|
| PostgreSQL | 16 | 7·9장 |
| Caddy | 2.10.2 | 9장 HTTPS 입구 |
| Prometheus | v3.15.0 | 8장 |
| Grafana | 13.2.4 | 8장 |
| k6 | 1.3.0 (`grafana/k6:1.3.0`) | 8장 부하 |
| cosign | v2.6.1 | 9장 이미지 서명 검증 |

## 코딩 에이전트 (10장)

| 소프트웨어 | 버전 |
|---|---|
| Claude Code | 2.1.306 |
| Codex CLI | 0.163.0 |
| OpenCode | 1.19.3 |

## 실행 환경

| 소프트웨어 | 버전 | 비고 |
|---|---|---|
| Python | 3.12 (Gateway 서버 3.12.3) | Windows 11에서는 3.12.9로 SDK 예제 확인 |
| uv | 0.13.1 | |
| Docker / Compose | 29.1.3 / v2.39.2 (Gateway 서버) | GPU 서버 28.x |
| Node.js | 22 | 4장 JS 예제, 10장 에이전트 이미지 |
| OS | Ubuntu 24.04 (Gateway), 22.04 (GPU 서버) | |
