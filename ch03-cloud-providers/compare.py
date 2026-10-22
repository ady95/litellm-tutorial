"""03-4. 하나의 CLI로 여러 제공자 응답 비교

사용: python compare.py "질문" [--repeat 3]
"""
import argparse
import statistics

from llm_client import MODELS, ask


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt")
    parser.add_argument("--repeat", type=int, default=1)
    args = parser.parse_args()

    print(f"질문: {args.prompt}\n")
    print(f"{'별칭':8} {'모델':38} {'지연(중앙값)':>12} {'입력':>5} {'출력':>5} {'비용(USD)':>10}")
    answers = {}
    for alias, params in MODELS.items():
        if None in params.values():   # 환경변수에 키가 없는 별칭은 건너뛴다
            print(f"{alias:8} (키 없음, 건너뜀)")
            continue
        runs = [ask(alias, args.prompt) for _ in range(args.repeat)]
        last = runs[-1]
        answers[alias] = last.text
        median = statistics.median(r.seconds for r in runs)
        cost = f"{last.cost_usd:.6f}" if last.cost_usd is not None else "-"
        print(f"{alias:8} {last.model:38} {median:>10.2f}초 {last.input_tokens:>5} {last.output_tokens:>5} {cost:>10}")

    print()
    for alias, text in answers.items():
        print(f"[{alias}] {text}\n")


if __name__ == "__main__":
    main()
