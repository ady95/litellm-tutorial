# 10장. 실전 프로젝트: 하이브리드 AI 에이전트 Gateway

검증 환경: LiteLLM 1.106.1 (9장 운영 구성), vLLM 0.31.0 + Qwen3.5-9B (RTX 3090, 32k), Claude Code 2.1.306, Codex CLI 0.163.0, OpenCode 1.19.3

## 준비

1. 9장 운영 구성을 띄우고 `config.yaml`을 이 폴더의 것으로 바꾼다 (`docker compose up -d --force-recreate litellm`). 10-4 측정은 `config.yaml`, 최종 운영은 `local-private`을 더한 `config-final.yaml`
2. 9장 `make_certs.sh`로 만든 `certs/ca.crt`를 이 폴더에 `gateway.crt`로 복사
3. 에이전트 이미지 빌드: `docker build -t litellm-book-agents:1 agent/`
4. vLLM을 32k로 다시 띄운다 (5장의 `vllm` 컨테이너가 있으면 먼저 `docker rm -f vllm`)

## 에이전트 하나 실행

```bash
GATEWAY_HOST=<Gateway> LITELLM_API_KEY=<가상 키> ./agent/run_agent.sh claude smart ./work "stats.py의 버그를 고치세요"
```

- `./work`는 지워도 되는 복사본을 쓴다. 에이전트는 그 안의 파일을 권한 확인 없이 고치고 명령을 실행한다.
- 컨테이너 안의 실행 사용자는 작업 폴더 소유자의 UID/GID로 맞춘다. 폴더 권한을 넓히지 않는다. root 소유 폴더는 쓰지 않는다.
- 컨테이너에는 Gateway 주소와 가상 키가 들어간다. 가상 키는 허용 모델과 예산을 제한해서 발급한다(7장).

## 벤치마크

```bash
export GATEWAY_HOST=<Gateway> LITELLM_MASTER_KEY=<마스터 키>   # 관리 입구(127.0.0.1:8444)가 있는 Gateway 서버에서
python bench_agents.py matrix results/results_matrix.jsonl            # 에이전트 3 × 별칭 4 (과제 t1)
python bench_agents.py scenario results/results_scenario.jsonl claude 1   # 시나리오 A·A2·B·C·D × 과제 5
python aggregate.py results/results_scenario.jsonl <9장-compose-폴더> <compose-프로젝트-이름> > results/summary.json
```

## 파일

| 파일 | 페이지 | 내용 |
|---|---|---|
| `config.yaml` | 10-1 | 에이전트용 Gateway 설정, 10-4 측정용 (local 32k, fast, smart, gemini) |
| `config-final.yaml` | 10-5 | 최종 운영 구성 (`local-private` 추가, Fallback 없음) |
| `agent/` | 10-1, 10-2 | 에이전트 이미지, 인증서 처리, Codex·OpenCode 설정, 실행 스크립트 |
| `tasks/` | 10-1 | 코딩 과제 5개 (지시문, 시작 코드, 숨은 테스트) |
| `bench_agents.py` | 10-2~10-4 | 호환성 시험과 시나리오 BMT 실행기 |
| `aggregate.py` | 10-4 | 결과와 Gateway DB 비용 집계. 조회 실패·기록 누락 시 중단, 키별 집계를 `per_key_usage.json`으로 저장 |
| `results/` | 10-2~10-5 | 원자료 (matrix 14회, scenario 75회, 요약, GPU 전력) |

## 원자료의 한계

- `summary.json`의 비용·토큰은 모든 실행이 끝난 뒤 Gateway DB에서 키별로 집계한 값이다. 그때의 키별 집계 원본은 보존하지 않았고 측정 서버도 정리했으므로, 공개 자료로는 최종 비용을 독립적으로 다시 계산할 수 없다. JSONL의 `cost_usd`는 실행 직후 읽은 값이라 DB 반영 전 금액이다.
- D 시나리오의 시간은 분류 호출 시간(`classify_seconds`)을 더해 JSONL에서 다시 계산했다(2026-10-22 검수 반영).
- 지금의 `aggregate.py`로 다시 측정하면 `per_key_usage.json`이 함께 생겨 이 한계가 없다.
