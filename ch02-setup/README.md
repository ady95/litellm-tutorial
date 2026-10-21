# 2장. LiteLLM 설치와 개발환경 구축

검증 환경: Ubuntu 24.04 / Python 3.12 / LiteLLM 1.106.1 / Docker 29.1 (Windows 11 기본 Python에서도 SDK 예제 동작 확인)

## 준비

```bash
uv venv --python 3.12
source .venv/bin/activate          # Windows: .venv\Scripts\activate
uv pip install "litellm==1.106.1" python-dotenv
cp ../.env.example .env            # OPENAI_API_KEY, LITELLM_MASTER_KEY 입력
```

## 파일

| 파일 | 페이지 | 내용 |
|---|---|---|
| `first_call.py` | 02-2 | SDK 첫 호출, 토큰·비용 확인 |
| `stream_call.py` | 02-2 | 스트리밍 응답 |
| `config.yaml` | 02-3 | Proxy 모델 목록 (gpt-6-luna, gpt-6.1-sol) |
| `proxy_call.py` | 02-3 | OpenAI SDK의 base_url을 Proxy로 바꿔 호출 |
| `error_cases.py` | 02-4 | 인증·네트워크·모델명 오류 재현 |

## Proxy 실행

```bash
docker run -d --name litellm-proxy \
  -v $(pwd)/config.yaml:/app/config.yaml \
  --env-file .env \
  -p 4000:4000 \
  docker.litellm.ai/berriai/litellm:v1.106.1 --config /app/config.yaml
```
