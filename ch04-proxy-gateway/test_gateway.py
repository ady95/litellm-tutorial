"""04-4. Gateway 통합 테스트 — 실행: pytest -v test_gateway.py"""
import json
import os

import openai
import pytest
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.environ.get("LITELLM_BASE_URL", "http://localhost:4000")
ALIASES = ["fast", "smart", "gemini"]


@pytest.fixture(scope="module")
def client():
    return openai.OpenAI(base_url=BASE_URL, api_key=os.environ["LITELLM_MASTER_KEY"])


def test_aliases_are_listed(client):
    ids = {m.id for m in client.models.list().data}
    assert set(ALIASES) <= ids


@pytest.mark.parametrize("alias", ALIASES)
def test_alias_answers(client, alias):
    response = client.chat.completions.create(
        model=alias,
        messages=[{"role": "user", "content": "숫자 7을 아라비아 숫자 하나로만 답하세요."}],
    )
    assert "7" in response.choices[0].message.content


@pytest.mark.parametrize("alias", ALIASES)
def test_tool_calling(client, alias):
    tool = {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "도시의 현재 날씨를 조회한다",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    }
    response = client.chat.completions.create(
        model=alias,
        messages=[{"role": "user", "content": "서울 날씨 알려줘"}],
        tools=[tool],
    )
    call = response.choices[0].message.tool_calls[0]
    assert call.function.name == "get_weather"
    assert json.loads(call.function.arguments)["city"] == "서울"


def test_rejects_wrong_key():
    anonymous = openai.OpenAI(base_url=BASE_URL, api_key="sk-not-a-real-key")
    with pytest.raises(openai.APIStatusError) as error:
        anonymous.models.list()
    # DB 없이 띄운 Proxy는 400(No connected db), 7장처럼 DB를 연결하면 401
    assert error.value.status_code in (400, 401)


def test_rejects_unknown_model(client):
    with pytest.raises(openai.BadRequestError):
        client.chat.completions.create(
            model="no-such-model",
            messages=[{"role": "user", "content": "hi"}],
        )
