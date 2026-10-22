#!/usr/bin/env bash
# 10장. 에이전트 하나를 Gateway의 별칭 하나로 실행한다 (작업 폴더는 /work에 마운트)
# 사용: GATEWAY_HOST=<주소> LITELLM_API_KEY=<가상 키> ./run_agent.sh <claude|codex|opencode> <별칭> <작업 폴더> "<지시문>"
# 작업 폴더는 지워도 되는 복사본을 쓴다. 에이전트는 그 안의 파일을 권한 확인 없이 고친다
set -euo pipefail
AGENT=$1; MODEL=$2; WORK=$(realpath "$3"); PROMPT=$4
HERE=$(dirname "$(realpath "$0")")
CERT=${GATEWAY_CERT:-$HERE/../gateway.crt}
URL=https://$GATEWAY_HOST:8443

case $AGENT in
  claude)
    CMD=(claude -p "$PROMPT" --dangerously-skip-permissions --output-format json)
    ENVS=(-e ANTHROPIC_BASE_URL="$URL" -e ANTHROPIC_AUTH_TOKEN="$LITELLM_API_KEY"
          -e ANTHROPIC_MODEL="$MODEL" -e ANTHROPIC_DEFAULT_HAIKU_MODEL="$MODEL" -e ANTHROPIC_SMALL_FAST_MODEL="$MODEL"
          -e CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
          -e CLAUDE_CODE_MAX_OUTPUT_TOKENS=8192) ;;   # 기본 32000은 로컬 모델(32k 컨텍스트)을 넘는다
  codex)
    mkdir -p "$WORK/.agent-home/.codex"
    sed "s#GATEWAY_HOST#$GATEWAY_HOST#; s#^model = .*#model = \"$MODEL\"#" "$HERE/codex-config.toml" > "$WORK/.agent-home/.codex/config.toml"
    CMD=(env HOME=/work/.agent-home codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox "$PROMPT")
    ENVS=(-e LITELLM_API_KEY="$LITELLM_API_KEY") ;;
  opencode)
    sed "s#GATEWAY_HOST#$GATEWAY_HOST#; s#\"litellm/fast\"#\"litellm/$MODEL\"#" "$HERE/opencode.json" > "$WORK/opencode.json"
    CMD=(opencode run "$PROMPT")
    ENVS=(-e LITELLM_API_KEY="$LITELLM_API_KEY") ;;
esac

# 컨테이너의 실행 사용자를 작업 폴더 소유자에 맞춘다 (폴더에 다른 사용자 쓰기 권한을 주지 않는다)
docker run --rm -v "$WORK":/work -w /work -v "$CERT":/certs/gateway.crt:ro "${ENVS[@]}" \
  -e AGENT_UID="$(stat -c %u "$WORK")" -e AGENT_GID="$(stat -c %g "$WORK")" \
  litellm-book-agents:1 "${CMD[@]}"
