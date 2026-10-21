# 1장. LiteLLM과 AI Gateway 이해하기

검증 환경: Ubuntu 24.04 / Python 3.12 / LiteLLM Proxy 1.106.1

## 실행

4장(또는 5장) 구성의 Gateway가 `http://localhost:4000`에서 실행 중이어야 합니다.

```bash
uv pip install httpx python-dotenv
python direct_vs_gateway.py
```

`.env`에 필요한 값: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `LITELLM_MASTER_KEY`

## 파일

| 파일 | 페이지 | 내용 |
|---|---|---|
| `direct_vs_gateway.py` | 01-5 | 제공자 직접 호출과 Gateway 경유 호출의 코드·지연 비교 |
