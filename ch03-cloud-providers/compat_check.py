"""03-2. 기능 호환성 검사: Streaming, Tool Calling, Structured Output, JSON 모드"""
import json

from dotenv import load_dotenv
import litellm

load_dotenv()
litellm.suppress_debug_info = True

MODELS = [
    "openai/gpt-6-luna",
    "anthropic/claude-sonnet-5-5",
    "openrouter/google/gemini-3.8-flash",
]

WEATHER_TOOL = {
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

CITY_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "city_info",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
                "country": {"type": "string"},
                "population_million": {"type": "number"},
            },
            "required": ["city", "country", "population_million"],
            "additionalProperties": False,
        },
    },
}


def check_stream(model):
    text = ""
    for chunk in litellm.completion(
        model=model,
        messages=[{"role": "user", "content": "1부터 5까지 쉼표로 이어서 쓰세요."}],
        stream=True,
    ):
        text += chunk.choices[0].delta.content or ""
    return text.strip()


def check_tool(model):
    response = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": "서울 날씨 알려줘"}],
        tools=[WEATHER_TOOL],
    )
    call = response.choices[0].message.tool_calls[0]
    return f"{call.function.name}({json.loads(call.function.arguments)})"


def check_tool_roundtrip(model):
    """도구 호출을 받고, 도구 결과를 다시 보내 최종 답까지 받는다."""
    messages = [{"role": "user", "content": "서울 날씨 알려줘"}]
    first = litellm.completion(model=model, messages=messages,
                               tools=[WEATHER_TOOL])
    message = first.choices[0].message
    call = message.tool_calls[0]
    messages.append(message.model_dump())
    result = {"city": "서울", "temp_c": 18, "sky": "맑음"}
    messages.append({"role": "tool", "tool_call_id": call.id,
                     "content": json.dumps(result, ensure_ascii=False)})
    final = litellm.completion(model=model, messages=messages,
                               tools=[WEATHER_TOOL])
    answer = final.choices[0].message.content or ""
    assert "18" in answer, f"도구 결과(18도)가 답에 없음: {answer[:60]}"
    return " ".join(answer.split())[:50]


def check_schema(model):
    response = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": "대한민국 수도 정보를 알려줘"}],
        response_format=CITY_SCHEMA,
    )
    return json.loads(response.choices[0].message.content)


def check_json_mode(model):
    response = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": "서울과 부산의 인구를 JSON으로 답하세요."}],
        response_format={"type": "json_object"},
    )
    return list(json.loads(response.choices[0].message.content))


CHECKS = [
    ("Streaming", check_stream),
    ("Tool Calling", check_tool),
    ("Tool 결과 반영", check_tool_roundtrip),
    ("Structured Output", check_schema),
    ("JSON 모드", check_json_mode),
]

for model in MODELS:
    print(f"=== {model}")
    for name, check in CHECKS:
        try:
            print(f"  {name:18} OK    {check(model)}")
        except Exception as e:
            print(f"  {name:18} 실패  {type(e).__name__}: {str(e)[:80]}")
