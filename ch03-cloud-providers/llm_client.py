"""03-3. 공통 호출 유틸리티 — 별칭으로 모델을 고르고, 결과를 같은 모양으로 돌려준다"""
import os
import time
from dataclasses import dataclass
from pathlib import Path

import litellm
import yaml
from dotenv import load_dotenv

load_dotenv()
litellm.suppress_debug_info = True

CONFIG_PATH = Path(__file__).with_name("models.yaml")


@dataclass
class Answer:
    alias: str
    model: str
    text: str
    seconds: float
    input_tokens: int
    output_tokens: int
    cost_usd: float | None


def _resolve(value):
    """config의 'os.environ/이름' 표기를 실제 환경변수 값으로 바꾼다.
    변수가 없거나 빈 값(공백만 있는 값 포함)이면 None으로 둔다. .env.example을 복사해 비워 둔 키도 여기에 해당한다."""
    if isinstance(value, str) and value.startswith("os.environ/"):
        return (os.environ.get(value.removeprefix("os.environ/")) or "").strip() or None
    return value


def load_models(path=CONFIG_PATH):
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return {alias: {k: _resolve(v) for k, v in params.items()} for alias, params in raw.items()}


MODELS = load_models()


def _cost(response):
    try:
        return litellm.completion_cost(completion_response=response)
    except Exception:
        # 가격표에 없는 모델(예: OpenRouter 경유)은 제공자가 알려 준 비용을 쓴다
        return response._hidden_params.get("response_cost")


def ask(alias, prompt, system=None, **options):
    params = MODELS[alias]
    missing = [k for k, v in params.items() if v is None]
    if missing:   # 키가 없는 별칭은 쓸 때만 오류를 낸다 (다른 별칭은 그대로 쓸 수 있다)
        raise RuntimeError(f"{alias}: models.yaml의 {missing} 값에 해당하는 환경변수가 없습니다")
    messages = [{"role": "system", "content": system}] if system else []
    messages.append({"role": "user", "content": prompt})

    start = time.time()
    response = litellm.completion(
        messages=messages,
        drop_params=True,   # 모델이 지원하지 않는 파라미터는 빼고 보낸다
        num_retries=2,
        timeout=60,
        **params,
        **options,
    )
    return Answer(
        alias=alias,
        model=params["model"],
        text=response.choices[0].message.content,
        seconds=round(time.time() - start, 2),
        input_tokens=response.usage.prompt_tokens,
        output_tokens=response.usage.completion_tokens,
        cost_usd=_cost(response),
    )


if __name__ == "__main__":
    for alias, params in MODELS.items():
        if None in params.values():   # 키가 없는 별칭은 건너뛴다
            print(f"{alias}: 키 없음, 건너뜀")
            continue
        print(ask(alias, "LiteLLM을 한 문장으로 설명하세요.", temperature=0.2))
