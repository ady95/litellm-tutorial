# 9장. 안전한 LiteLLM 운영환경 구축하기

검증 환경: LiteLLM Proxy 1.106.1(digest 고정), Caddy 2.10.2, PostgreSQL 16, cosign 2.6.1

## 구성

```text
인터넷/사내망 ──HTTPS 8443──▶ Caddy ──▶ LiteLLM (포트 미공개, 워커 4) ──▶ PostgreSQL (내부망 전용)
서버 안에서만 ──HTTP 127.0.0.1:8444──▶ Caddy ──▶ LiteLLM (관리 API·UI)
```

```bash
# 시험용 사설 CA + 서버 인증서 (운영에서는 공인 인증서나 사내 CA 사용)
./make_certs.sh <Gateway-서버-IP>
cp .env.example .env   # 값 채우기
docker compose up -d
```

클라이언트에는 `certs/ca.crt`를 신뢰하도록 설정합니다. `openssl req -x509` 한 줄로 만든 자체 서명 인증서(CA:TRUE)는 rustls 기반 클라이언트(Codex CLI 등)가 거부합니다.

## 파일

| 파일 | 페이지 | 내용 |
|---|---|---|
| `docker-compose.yaml` | 09-1 | Caddy + LiteLLM(digest 고정) + PostgreSQL(internal 네트워크) |
| `make_certs.sh` | 09-1 | 시험용 사설 CA와 서버 인증서 |
| `Caddyfile` | 09-1 | 공개 입구는 모델 호출 경로만, 관리 입구는 127.0.0.1 |
| `config.yaml` | 09-1 | 모델 설정 (7장과 같음) |
| `key_ops.py` | 09-2, 09-3 | 키 차단·해제·삭제·재발급, Enterprise 기능 경계 시험 (서버 안에서 실행) |
| `verify_image.sh` | 09-4 | cosign으로 LiteLLM 이미지 서명 검증 |
| `backup.sh` | 09-5 | pg_dump 백업 |
