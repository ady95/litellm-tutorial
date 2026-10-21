#!/usr/bin/env bash
# 09-5. LiteLLM DB 백업 (가상 키, 팀, 예산, 사용 기록)
# 복구: docker compose exec -T db pg_restore -U litellm -d litellm --no-owner < backup/litellm-<시각>.dump
set -euo pipefail
mkdir -p backup
FILE=backup/litellm-$(date +%Y%m%d-%H%M%S).dump
# exec는 표준 입력을 읽으므로 스크립트 안에서는 </dev/null로 막는다
docker compose exec -T db pg_dump -U litellm -d litellm -Fc < /dev/null > "$FILE"
chmod 600 "$FILE"
echo "saved $FILE ($(stat -c %s "$FILE") bytes)"
