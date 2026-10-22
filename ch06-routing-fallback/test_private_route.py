"""06-4-1·06-5. 민감정보 경로 회귀 시험 (서버 없이 실행)

1) 민감정보가 보이면 정책 엔진이 local-private을 고르는가
2) 설정 파일에서 local-private이 어떤 Fallback에도 들어 있지 않은가

실행: python test_private_route.py
"""
import os
import sys
from pathlib import Path

import yaml

os.environ.setdefault("LITELLM_MASTER_KEY", "sk-offline-test")   # 서버에 연결하지 않음
import policy_engine  # noqa: E402

HERE = Path(__file__).parent
CONFIGS = [HERE / "config-local-first.yaml", HERE / "config-auto.yaml",
           HERE.parent / "ch10-agent-gateway" / "config-final.yaml"]
SENSITIVE_PROMPTS = [
    "제 번호는 010-1234-5678입니다. 이 번호로 예약 확인 문자를 써 주세요.",
    "kim@example.com 주소로 보낼 사과 메일을 써 주세요.",
    "900101-1234567 고객의 가입 내역을 정리해 주세요.",
]


def fallback_names(settings):
    names = set()
    for key in ("fallbacks", "context_window_fallbacks", "content_policy_fallbacks"):
        for item in settings.get(key) or []:
            for src, targets in item.items():
                names.add(src)
                names.update(targets)
    names.update(settings.get("default_fallbacks") or [])
    return names


def main():
    failed = 0
    for prompt in SENSITIVE_PROMPTS:
        alias, reason = policy_engine.choose_alias(prompt)   # 민감정보는 분류기를 부르지 않는다
        ok = alias == "local-private"
        failed += not ok
        print(f"{'OK  ' if ok else 'FAIL'} 정책 엔진 → {alias:14} ({reason}) {prompt[:24]}")

    for path in CONFIGS:
        config = yaml.safe_load(path.read_text(encoding="utf-8"))
        models = {m["model_name"] for m in config["model_list"]}
        names = set()
        for section in ("router_settings", "litellm_settings"):
            names |= fallback_names(config.get(section) or {})
        has_alias = "local-private" in models
        no_fallback = "local-private" not in names
        ok = has_alias and no_fallback
        failed += not ok
        print(f"{'OK  ' if ok else 'FAIL'} {path.parent.name}/{path.name}: "
              f"별칭 {'있음' if has_alias else '없음'}, Fallback {'없음' if no_fallback else '있음'}")

    print("\n통과" if not failed else f"\n실패 {failed}건")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
