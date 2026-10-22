"""06-4. 내장 난이도 라우터가 질문을 어느 모델로 보내는지 확인한다

사람이 미리 정한 기대 등급과 라우터의 선택을 비교한다.
"""
import os
from collections import Counter

import httpx
from dotenv import load_dotenv

load_dotenv()
GATEWAY = os.environ.get("LITELLM_BASE_URL", "http://localhost:4000")
HEADERS = {"Authorization": f"Bearer {os.environ['LITELLM_MASTER_KEY']}"}
TIER_TO_ALIAS = {"SIMPLE": "local", "MEDIUM": "fast",
                 "COMPLEX": "smart", "REASONING": "smart"}

PROMPTS = [
    ("SIMPLE", "안녕하세요", "Hello"),
    ("SIMPLE", "1 더하기 1은?", "What is 1 plus 1?"),
    ("SIMPLE", "프랑스의 수도는?", "What is the capital of France?"),
    ("MEDIUM", "RAG와 파인튜닝의 차이를 설명해 주세요.", "Explain the difference between RAG and fine-tuning."),
    ("MEDIUM", "회의 일정 변경을 알리는 짧은 이메일을 써 주세요.", "Write a short email announcing a meeting reschedule."),
    ("MEDIUM", "파이썬 리스트 컴프리헨션 예시를 보여 주세요.", "Show an example of a Python list comprehension."),
    ("COMPLEX",
     "다음 코드의 버그를 찾아 고치고 테스트를 작성해 주세요:\n```python\ndef avg(xs):\n    return sum(xs) / len(xs)\n```",
     "Find and fix the bug in this code and write unit tests:\n```python\ndef avg(xs):\n    return sum(xs) / len(xs)\n```"),
    ("COMPLEX",
     "마이크로서비스 환경에서 사가 패턴과 2단계 커밋을 비교하고, 주문·결제·재고 시스템에 맞는 설계를 제안해 주세요.",
     "Compare the saga pattern and two-phase commit in microservices, and propose a design for an order, payment and inventory system."),
    ("COMPLEX",
     "Kubernetes에서 LiteLLM Gateway를 고가용성으로 배포하는 아키텍처를 설계하고 장애 시나리오별 대응을 설명해 주세요.",
     "Design a highly available Kubernetes architecture for a LiteLLM gateway and explain how it handles each failure scenario."),
    ("REASONING", "단계별로 생각해서 루트 2가 무리수임을 증명해 주세요.", "Think step by step and prove that the square root of 2 is irrational."),
    ("REASONING",
     "단계별로 추론해 주세요. 세 사람 중 한 명만 진실을 말합니다. A는 B가 거짓말쟁이라고 하고, B는 C가 거짓말쟁이라고 하고, C는 A와 B 모두 거짓말쟁이라고 합니다. 누가 진실을 말하나요?",
     "Reason step by step. Exactly one of three people tells the truth. A says B lies, B says C lies, C says both A and B lie. Who tells the truth?"),
    ("REASONING", "단계별로 계산해 주세요: 연 5% 복리로 1000만 원을 10년 예치하면 얼마가 되나요?",
     "Calculate step by step: how much will 10 million won become after 10 years at 5% annual compound interest?"),
]


def routed_tier(prompt):
    """라우터가 고른 등급과 점수를 응답 헤더에서 읽는다."""
    r = httpx.post(f"{GATEWAY}/v1/chat/completions", headers=HEADERS, timeout=120,
                   json={"model": "auto", "max_tokens": 16,
                         "messages": [{"role": "user", "content": prompt}]})
    tier = r.headers.get("x-litellm-complexity-router-tier", f"?{r.status_code}")
    score = float(r.headers.get("x-litellm-complexity-router-score", "nan"))
    return tier, score


if __name__ == "__main__":
    hits = Counter()
    print(f"{'기대 등급':10} {'한국어 판정':16} {'영어 판정':16}  질문")
    for expected, ko, en in PROMPTS:
        (tier_ko, score_ko), (tier_en, score_en) = routed_tier(ko), routed_tier(en)
        hits["ko"] += tier_ko == expected
        hits["en"] += tier_en == expected
        print(f"{expected:10} {tier_ko:9}{score_ko:+.2f}   {tier_en:9}{score_en:+.2f}   {en[:40]}")
    print(f"\n기대 등급과 일치: 한국어 {hits['ko']}/{len(PROMPTS)}, 영어 {hits['en']}/{len(PROMPTS)}")
