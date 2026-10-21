#!/usr/bin/env bash
# 09-4. LiteLLM 공식 이미지의 cosign 서명 검증
# 공개 키는 공식 보안 공지가 안내한 고정 커밋의 cosign.pub을 쓴다
set -euo pipefail
IMAGE=${1:-docker.litellm.ai/berriai/litellm:v1.106.1}
KEY=https://raw.githubusercontent.com/BerriAI/litellm/0112e53046018d726492c814b3644b7d376029d0/cosign.pub
docker run --rm ghcr.io/sigstore/cosign/cosign:v2.6.1 verify --key "$KEY" "$IMAGE"
