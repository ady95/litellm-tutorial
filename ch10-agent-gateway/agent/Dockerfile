# 10장. 코딩 에이전트 3종을 버전 고정으로 담은 실행 환경
FROM node:22-bookworm
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       python3-pytest git ca-certificates sudo \
    && rm -rf /var/lib/apt/lists/*
RUN npm install -g @anthropic-ai/claude-code@2.1.306 \
    @openai/codex@0.163.0 opencode-ai@1.19.3
# Gateway가 자체 서명 인증서를 쓰는 경우 /certs/gateway.crt를 마운트하면 신뢰 목록에 추가한다
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
