# 3장. 하나의 API로 여러 클라우드 LLM 사용하기

검증 환경: Ubuntu 24.04 / Python 3.12 / LiteLLM 1.106.1

## 준비

```bash
uv pip install "litellm[mcp]==1.106.1" python-dotenv pyyaml
```

LiteLLM 1.106.0~1.106.1에서는 `tools`를 넘기는 호출이 `No module named 'mcp'`로 실패합니다([#46045](https://github.com/BerriAI/litellm/issues/46045)). `[mcp]`를 붙여 설치하면 해결됩니다.

`.env`에 필요한 키:

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OPENROUTER_API_KEY=sk-or-...
```

## 파일

| 파일 | 페이지 | 내용 |
|---|---|---|
| `providers.py` | 03-1 | 같은 요청을 OpenAI·Anthropic·Gemini(OpenRouter)에 보내기 |
| `compat_check.py` | 03-2 | Streaming·Tool Calling·Structured Output·JSON 모드 검사 |
| `models.yaml`, `llm_client.py` | 03-3 | 별칭 기반 공통 호출 유틸리티 |
| `compare.py` | 03-4 | 여러 제공자 응답 비교 CLI |
