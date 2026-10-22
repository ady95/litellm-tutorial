"""06-4-1. Gateway 앞에 두는 별도 라우팅 정책 엔진

1) 민감정보가 보이면 Fallback이 없는 local-private으로 (외부 전송 금지)
2) 그 밖에는 로컬 소형 분류기(LLM)에게 난이도를 물어 별칭을 고른다

정규식은 형식이 뻔한 일부 개인정보만 잡는다. 모든 민감정보를 탐지한다는 보장이 아니다.
다른 프로그램에서 모듈로 가져다 쓸 때는 시작할 때 require_private_alias()를 한 번 호출한다.
"""
import json
import os
import re
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    base_url=os.environ.get("LITELLM_BASE_URL", "http://localhost:4000"),
    api_key=os.environ["LITELLM_MASTER_KEY"],
)

PRIVATE_ALIAS = "local-private"   # Gateway 설정에서 fallbacks에 넣지 않은 별칭
TIER_TO_ALIAS = {"SIMPLE": "local", "MEDIUM": "fast",
                 "COMPLEX": "smart", "REASONING": "smart"}
SENSITIVE = [
    re.compile(r"\d{6}-[1-4]\d{6}"),            # 주민등록번호 형식
    re.compile(r"01[016789]-?\d{3,4}-?\d{4}"),  # 휴대전화 번호
    re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"),     # 이메일 주소
]
RUBRIC = """사용자 요청의 난이도를 하나로 분류한다.
SIMPLE: 인사, 단순 사실, 한 줄 계산
MEDIUM: 개념 설명, 짧은 글쓰기, 간단한 코드 예시
COMPLEX: 코드 디버깅·테스트 작성, 설계, 여러 기술의 비교·제안
REASONING: 증명, 논리 퍼즐, 여러 단계의 계산"""
SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "tier",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "tier": {"type": "string", "enum": list(TIER_TO_ALIAS)},
            },
            "required": ["tier"],
            "additionalProperties": False,
        },
    },
}


def classify(prompt):
    response = client.chat.completions.create(
        model="local",
        messages=[{"role": "system", "content": RUBRIC},
                  {"role": "user", "content": prompt}],
        response_format=SCHEMA,
        max_tokens=50,
    )
    return json.loads(response.choices[0].message.content)["tier"]


def require_private_alias():
    """Gateway에 local-private이 없으면 민감정보를 보낼 곳이 없으므로
    시작하지 않는다."""
    names = {m.id for m in client.models.list().data}
    if PRIVATE_ALIAS not in names:
        raise SystemExit(f"Gateway에 '{PRIVATE_ALIAS}' 별칭이 없습니다. "
                         "config.yaml에 Fallback 없이 추가하세요.")


def choose_alias(prompt):
    """(별칭, 이유)를 돌려준다."""
    if any(p.search(prompt) for p in SENSITIVE):
        return PRIVATE_ALIAS, "민감정보"
    tier = classify(prompt)
    return TIER_TO_ALIAS[tier], tier


def ask(prompt):
    alias, reason = choose_alias(prompt)
    # local-private이 실패하면 오류를 그대로 올린다. 다른 별칭으로 다시 보내지 않는다.
    response = client.chat.completions.create(model=alias, messages=[{"role": "user", "content": prompt}])
    return alias, reason, response.choices[0].message.content


if __name__ == "__main__":
    from complexity_probe import PROMPTS

    require_private_alias()
    hits, seconds = {"ko": 0, "en": 0}, []
    print(f"{'기대 등급':10} {'한국어 판정':12} {'영어 판정':12}  질문")
    for expected, ko, en in PROMPTS:
        row = []
        for lang, prompt in (("ko", ko), ("en", en)):
            start = time.time()
            tier = classify(prompt)
            seconds.append(time.time() - start)
            hits[lang] += tier == expected
            row.append(tier)
        print(f"{expected:10} {row[0]:12} {row[1]:12}  {en[:40]}")
    print(f"\n기대 등급과 일치: 한국어 {hits['ko']}/{len(PROMPTS)}, 영어 {hits['en']}/{len(PROMPTS)}")
    print(f"분류 1회 평균 {sum(seconds) / len(seconds):.2f}초")

    print("\n민감정보 규칙:")
    for p in ("제 번호는 010-1234-5678입니다. 이 번호로 예약 확인 문자를 써 주세요.",
              "kim@example.com 주소로 보낼 사과 메일을 써 주세요."):
        print(" ", choose_alias(p), p[:30])
