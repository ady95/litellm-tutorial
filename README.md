# litellm-tutorial

위키독스 책 「LiteLLM 따라하기 — 로컬·클라우드 LLM 통합부터 AI Gateway 구축과 에이전트 연동까지」의 예제 코드 저장소입니다.

- 책: [https://wikidocs.net/book/21778](https://wikidocs.net/book/21778)

## 구성

```text
litellm-tutorial/
├── tested-versions.md      검증에 사용한 소프트웨어 버전
├── .env.example            환경변수 예시 (복사해서 .env로 사용)
├── ch01-concept/           1장 직접 호출과 Gateway 비교
├── ch02-setup/             2장 설치와 개발환경
├── ch03-cloud-providers/   3장 여러 클라우드 LLM
├── ch04-proxy-gateway/     4장 LiteLLM Proxy Gateway
├── ch05-local-llm/         5장 로컬 LLM 통합
├── ch06-routing-fallback/  6장 라우팅과 장애 복구
├── ch07-keys-budgets/      7장 키와 비용 관리
├── ch08-observability-bmt/ 8장 모니터링과 LiteLLM vs Bifrost BMT (측정 원자료 포함)
├── ch09-security-operations/ 9장 운영환경 보안
└── ch10-agent-gateway/     10장 하이브리드 에이전트 Gateway (측정 원자료 포함)
```

## 시작하기

```bash
git clone https://github.com/ady95/litellm-tutorial.git
cd litellm-tutorial
cp .env.example .env   # API 키 입력
```

각 장 디렉터리의 README에 실행 폴더, 필요한 환경변수, 먼저 해 둘 일이 있습니다. 장을 이어서 실습할 때는 앞 장의 컨테이너(`litellm-proxy`, `vllm`)가 같은 이름·포트를 쓰므로 먼저 지웁니다. 버전은 [tested-versions.md](tested-versions.md)에 고정된 값을 사용하세요.

## 주의

- 실제 API 키와 `.env` 파일은 절대 커밋하지 마세요.
- LiteLLM 1.82.7·1.82.8은 2026년 3월 공급망 침해가 확인된 버전이므로 설치하지 마세요. [공식 보안 공지](https://docs.litellm.ai/blog/security-update-march-2026)
