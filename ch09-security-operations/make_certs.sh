#!/usr/bin/env bash
# 09-1. 시험용 사설 CA와, 그 CA로 서명한 Gateway 서버 인증서를 만든다
# 자체 서명 인증서 하나로 끝내면 일부 클라이언트(rustls를 쓰는 Codex CLI 등)가 거부한다 (10-2)
# 사용: ./make_certs.sh <Gateway-서버-IP> [호스트명]
set -euo pipefail
IP=$1; NAME=${2:-litellm-gateway}
mkdir -p certs && cd certs

# 1. 사설 CA (클라이언트가 신뢰할 인증서: ca.crt)
openssl req -x509 -newkey rsa:2048 -nodes -days 365 -subj "/CN=LiteLLM Book Test CA" \
  -keyout ca.key -out ca.crt 2>/dev/null

# 2. 서버 인증서 (CA가 아님, 서버 인증 용도)
openssl req -newkey rsa:2048 -nodes -subj "/CN=$NAME" -keyout key.pem -out server.csr 2>/dev/null
cat > server.ext <<EOF
basicConstraints=critical,CA:FALSE
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=DNS:$NAME,IP:$IP
EOF
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -days 90 \
  -extfile server.ext -out cert.pem 2>/dev/null

chmod 600 ca.key key.pem; chmod 644 ca.crt cert.pem
rm -f server.csr server.ext
echo "Caddy: cert.pem, key.pem / 클라이언트가 신뢰할 CA: ca.crt"
