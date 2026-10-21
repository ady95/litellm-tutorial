# 7장. API 키와 LLM 사용 비용 관리하기

검증 환경: LiteLLM Proxy 1.106.1 + PostgreSQL 16 (Docker Compose), Python 3.12

## 실행

`.env` 예시 (값은 직접 생성):

```bash
LITELLM_MASTER_KEY=sk-...        # echo "sk-$(openssl rand -hex 32)"
LITELLM_SALT_KEY=sk-...          # 한 번 정하면 바꾸지 않는다 (DB 암호화 키)
POSTGRES_PASSWORD=...            # openssl rand -hex 16
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
VLLM_API_BASE=http://<GPU-서버-주소>:8000/v1
MOCK_API_BASE=http://host.docker.internal:8901/v1   # 6장 mock_llm.py
```

```bash
docker compose up -d
python keys_lab.py all      # 허용 모델, 예산, RPM, 팀 예산, 권한
python keys_lab2.py         # 기록 시점, 동시 요청, 재시작, 만료, TPM, 실제 비용
```

셸에 같은 이름의 환경변수가 export되어 있으면 Compose가 `.env`보다 우선합니다(02-4). 깨끗한 셸에서 실행하세요.

## 파일

| 파일 | 페이지 | 내용 |
|---|---|---|
| `docker-compose.yaml` | 07-1 | Proxy + PostgreSQL |
| `config.yaml` | 07-1, 07-3 | 모델 + 호출당 $0.01로 단가를 지정한 Mock 모델 |
| `keys_lab.py` | 07-1, 07-2, 07-4 | 가상 키·팀·예산·RPM·권한 시험 |
| `keys_lab2.py` | 07-3, 07-4 | 사용량 기록 시점, 동시 요청, 재시작, 만료, TPM, 실제 모델 비용 |
