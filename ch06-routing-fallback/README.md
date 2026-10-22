# 6장. 모델 라우팅과 장애 자동 복구 구현하기

검증 환경: LiteLLM Proxy 1.106.1, vLLM 0.31.0 (RTX 3090), Python 3.12

## Mock 서버

장애를 마음대로 일으키는 가짜 OpenAI 호환 서버입니다. 모델 이름으로 동작을 정합니다(`ok`, `ok-d500`, `e429`, `e500`, `flaky50`, `hang`).

```bash
uv pip install fastapi uvicorn httpx python-dotenv openai pyyaml
uvicorn mock_llm:app --host 0.0.0.0 --port 8901
```

`.env`에 `MOCK_API_BASE=http://host.docker.internal:8901/v1`을 추가하고, Proxy는 `--add-host=host.docker.internal:host-gateway`로 실행합니다.

## 파일

| 파일 | 페이지 | 내용 |
|---|---|---|
| `mock_llm.py` | 06-1~06-3 | 장애 주입용 Mock 서버 (8장에서도 사용) |
| `config-mock.yaml` | 06-1~06-3 | 가중치 분산, 재시도, Fallback, 타임아웃, 쿨다운 |
| `config-mock-latency.yaml` | 06-1 | 지연 기반 라우팅 |
| `config-mock-tuned.yaml` | 06-2 | 오류 유형별 재시도 정책 |
| `experiments.py` | 06-1~06-3 | 실험 실행 (`python experiments.py all`) |
| `config-auto.yaml`, `complexity_probe.py` | 06-4 | 내장 난이도 라우터(베타) 판정 확인 |
| `policy_engine.py` | 06-4-1 | 민감정보 규칙 + 로컬 LLM 분류기 정책 엔진. 민감정보는 Fallback 없는 `local-private`으로, 별칭이 없으면 시작하지 않음 |
| `test_private_route.py` | 06-4-1, 06-5 | 민감정보 경로 회귀 시험 (서버 없이 `python test_private_route.py`) |
| `config-local-first.yaml`, `failover_watch.py` | 06-5 | 로컬 우선 + 클라우드 Fallback 실습 |
