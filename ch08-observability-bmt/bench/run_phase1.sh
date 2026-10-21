#!/usr/bin/env bash
# 8장 BMT 1단계: Mock 백엔드 앞에서 Gateway 오버헤드와 처리 한계 측정
# 부하 발생 서버(Gateway와 다른 기기)에서 실행한다. Mock 서버(8901)도 이 서버에 띄워 둔다.
#
# 사용: GATEWAY_HOST=<Gateway 서버 주소> LITELLM_KEY=<마스터 키> ./run_phase1.sh <대상> [회차]
#   대상: direct | litellm | bifrost   (한 번에 하나의 Gateway만 켜 둘 것)
set -euo pipefail
TARGET=$1
ROUND=${2:-1}
RATES="50 100 200 400 800"
OUT=results/phase1.jsonl
mkdir -p results && chmod o+w results .

case $TARGET in
  direct)  URL=http://localhost:8901;          MODEL=ok;        KEY="" ;;
  litellm) URL=http://$GATEWAY_HOST:4000;      MODEL=bench;     KEY=$LITELLM_KEY ;;
  bifrost) URL=http://$GATEWAY_HOST:4001;      MODEL=openai/ok; KEY="" ;;
esac

k6() {  # $1=rate $2=duration
  docker run --rm --network host -v "$PWD":/scripts grafana/k6:1.3.0 run -q \
    -e TARGET="$URL" -e MODEL="$MODEL" -e KEY="$KEY" -e RATE="$1" -e DURATION="$2" \
    -e OUT=/scripts/results/last.json /scripts/load.js >/dev/null 2>&1
}

k6 20 10s   # 워밍업
for rate in $RATES; do
  k6 "$rate" 20s
  python3 - "$TARGET" "$ROUND" >> "$OUT" <<'EOF'
import json, sys
r = json.load(open("results/last.json"))
r.update(target=sys.argv[1], round=int(sys.argv[2]))
print(json.dumps(r))
EOF
  tail -1 "$OUT"
done
