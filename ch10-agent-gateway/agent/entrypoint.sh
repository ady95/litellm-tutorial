#!/usr/bin/env bash
# 인증서를 시스템 신뢰 목록에 넣은 뒤, 일반 사용자(node)로 명령을 실행한다
set -e
if [ -f /certs/gateway.crt ]; then
  cp /certs/gateway.crt /usr/local/share/ca-certificates/gateway.crt
  update-ca-certificates >/dev/null 2>&1
fi
export NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
# 작업 폴더 소유자와 같은 UID/GID로 실행한다. 호스트에서 폴더 권한을 넓히지 않아도 된다
if [ -n "${AGENT_UID:-}" ] && [ "$AGENT_UID" != "0" ] && [ "$AGENT_UID" != "$(id -u node)" ]; then
  groupmod -o -g "$AGENT_GID" node
  usermod -o -u "$AGENT_UID" -g "$AGENT_GID" node >/dev/null
fi
# 일부 에이전트는 root에서 권한 확인 생략 옵션을 거부하므로 node 사용자로 실행
exec sudo -E -u node HOME=/home/node "$@"
