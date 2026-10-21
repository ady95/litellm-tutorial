# 10장. 실전 프로젝트: 하이브리드 AI 에이전트 Gateway

검증 환경: LiteLLM 1.106.1 (9장 운영 구성), vLLM 0.31.0 + Qwen3.5-9B (RTX 3090, 32k), Claude Code 2.1.306, Codex CLI 0.163.0, OpenCode 1.19.3

## 준비

1. 9장 운영 구성을 띄우고 `config.yaml`을 이 폴더의 것으로 바꾼다 (`docker compose up -d --force-recreate litellm`)
2. 9장 `make_certs.sh`로 만든 `certs/ca.crt`를 이 폴더에 `gateway.crt`로 복사
3. 에이전트 이미지 빌드: `docker build -t litellm-book-agents:1 agent/`

## 에이전트 하나 실행

```bash
GATEWAY_HOST=<Gateway> LITELLM_API_KEY=<가상 키> ./agent/run_agent.sh claude smart ./work "stats.py의 버그를 고치세요"
```

## 벤치마크

```bash
export GATEWAY_HOST=<Gateway> LITELLM_MASTER_KEY=<마스터 키>   # 관리 입구(127.0.0.1:8444)가 있는 Gateway 서버에서
python bench_agents.py matrix results/results_matrix.jsonl            # 에이전트 3 × 별칭 4 (과제 t1)
python bench_agents.py scenario results/results_scenario.jsonl claude 1   # 시나리오 A·A2·B·C·D × 과제 5
python aggregate.py results/results_scenario.jsonl <9장-compose-폴더> > results/summary.json
```

## 파일

| 파일 | 페이지 | 내용 |
|---|---|---|
| `config.yaml` | 10-1 | 에이전트용 Gateway 설정 (local 32k, fast, smart, gemini) |
| `agent/` | 10-1, 10-2 | 에이전트 이미지, 인증서 처리, Codex·OpenCode 설정, 실행 스크립트 |
| `tasks/` | 10-1 | 코딩 과제 5개 (지시문, 시작 코드, 숨은 테스트) |
| `bench_agents.py` | 10-2~10-4 | 호환성 시험과 시나리오 BMT 실행기 |
| `aggregate.py` | 10-4 | 결과와 Gateway DB 비용 집계 |
| `results/` | 10-2~10-5 | 원자료 (matrix 14회, scenario 75회, 요약, GPU 전력) |
