# 4장. LiteLLM Proxy로 AI Gateway 구축하기

검증 환경: Ubuntu 24.04 / Docker 29.1 / LiteLLM Proxy 1.106.1 / Python 3.12 / Node.js 22

## Gateway 실행

`.env`에 `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`, `LITELLM_MASTER_KEY`를 넣고:

```bash
docker run -d --name litellm-proxy \
  -v $(pwd)/config.yaml:/app/config.yaml \
  --env-file .env \
  -p 4000:4000 \
  docker.litellm.ai/berriai/litellm:v1.106.1 --config /app/config.yaml
```

설정을 바꾸면 `docker restart litellm-proxy`로 다시 읽게 합니다.

## 파일

| 파일 | 페이지 | 내용 |
|---|---|---|
| `config.yaml` | 04-1, 04-2 | 별칭 3개(fast/smart/gemini) + OpenRouter 와일드카드 |
| `client.py` | 04-3 | OpenAI Python SDK로 호출, 응답 헤더의 비용·오버헤드 확인 |
| `client.mjs` | 04-3 | OpenAI Node SDK로 호출 (`npm install openai && node client.mjs`) |
| `test_gateway.py` | 04-4 | Gateway 통합 테스트 (`pytest -v test_gateway.py`) |
