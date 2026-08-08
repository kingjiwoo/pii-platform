# CLAUDE.md

프로젝트 컨텍스트 — Claude 세션 시작 시 이걸 기준으로 판단.

## 이 프로젝트가 뭔지 (한 줄)

금융권 컴플라이언스를 위한 **하이브리드 LLM 게이트웨이 on Kubernetes** — PII는 사내 vLLM으로, 일반 요청은 상용 API로 라우팅 + 비용·SLA 관측.

## 목적 (숨은 컨텍스트)

이건 **토스뱅크 ML Engineer (ML/LLM Ops) 지원용 사이드 프로젝트**임. 유일한 하드 게이트가 "K8s 위에서 서비스 개발·배포·운영 경험"이라 그걸 진짜로 채우는 게 최우선. 기술 선택·스코프 판단은 전부 이 목적에 종속.

## 원본 계획서

`~/Documents/Obsidian Vault/toss-llm-gateway/00-프로젝트-계획.md` — 문제 정의·아키텍처·**48개 상세 task**·백업안·결정 로그 전부 여기 있음. **작업 방향 헷갈리면 이것부터 다시 봐.**

---

## 📊 Progress (항상 최신 상태 유지)

> **규칙:** task를 시작할 때 `⏳ 진행중`, 끝나면 `✅ 완료`로 이 섹션 즉시 업데이트. PR 머지되면 PR 라인도 업데이트. 옵시디언 계획서의 체크박스도 함께 갱신.

**전체:** `18 / 52` task 완료 (35%)

| PR | 브랜치 | Task | 상태 |
|----|--------|------|------|
| PR 0 | `feat/settings` → develop (PR #1 머지 완료) | 8/8 | ✅ 완료 |
| PR 1 ⭐ | `feat/gateway` | 10/16 | ⏳ 진행중 |
| PR 2 | `feat/day2-vllm-on-k8s` | 0/7 | 🔒 잠김 |
| PR 3 | `feat/day3-sensitivity-routing` | 0/8 | 🔒 잠김 |
| PR 4 | `feat/day4-observability` | 0/6 | 🔒 잠김 |
| PR 5 | `feat/day5-ops-polish` | 0/7 | 🔒 잠김 |

**현재 위치:** PR 1 진행중. T1.1~T1.10 완료. **뱅크 K8s 필수요건 1차 확보 🎯** 다음 = T1.11 (kubectl 디버깅 4종 학습).

**마일스톤:**
- 🎯 **PR 1 완료** = 뱅크 K8s 필수요건 충족 (최우선)
- 🎯 **PR 3 완료** = 도메인 스토리(하이브리드 라우팅) 완성
- 🎯 **PR 5 완료** = 포트폴리오 완성

### 진행중 task (있으면)

_없음_

### 최근 완료 (최대 5개)

- ✅ **T1.10** 🎉 — `helm install gateway` 성공 → curl 스모크 200 응답 (`{"content":"Hello!"}`). 트래픽 전체 경로 검증. `scripts/smoke-gateway.sh` 재사용 스크립트 확보
- ✅ **T1.9** — ingress-nginx Controller 설치 완료 + `values.yaml`에서 Ingress 활성화 (`gateway.localtest.me`, `pathType: Prefix`)
- ✅ **T1.8** — ConfigMap + Secret 템플릿 추가, Deployment에 envFrom·volumeMount·checksum 트릭 적용. `helm template` 렌더링 검증 완료
- ✅ **T1.7** — `values.yaml` 우리 값으로 조정 (`pii-litellm:dev`, port 4000, `/health` probe). `helm template`로 렌더링 검증 완료
- ✅ **T1.6** — `helm create deploy/helm/litellm` + 생성 파일 순회 학습 (Chart.yaml, values.yaml, deployment.yaml)
- ✅ **T1.5** — 이미지 빌드 `pii-litellm:dev` (385MB) + `kind load` 완료. 노드 containerd 캐시에서 확인
- ✅ **T1.4** — `docker/litellm/Dockerfile` (베이스 `main-latest` + config COPY + `--config /app/config.yaml --port 4000`)
- ✅ **T1.3** — `docker/litellm/config.yaml` (gpt-4o-mini만, `os.environ/*`로 API key·master key 참조)
- ✅ **T1.2** — `deploy/kind/kind-config.yaml` (control-plane 1개, 80/443 hostPort, `ingress-ready=true` 라벨) + 스모크 검증
- ✅ **T1.1** — kind 도구 설치 (`kind v0.32.0`, `helm v4.2.3`) + 개념 학습 문서
- ✅ T0.8 — 첫 PR 머지 완료 (PR #1: feat/settings → develop, 머지 커밋 `4656a2b`) 🎉 PR 0 종료

### 결정·트러블 로그

- 브랜치명 `feat/settings` 유지 (계획서는 `chore/initial-setup`). 이름보다 진도 우선.
- `/new-branch` 슬래시 커맨드 재생성 스킵 — 사용자가 브랜치 직접 만들기로 함.
- **아키텍처 변경: FastAPI 서비스 레이어 추가** (2026-08-08). PII·auth·라우팅 결정 = FastAPI, LLM 어댑터 = LiteLLM으로 계층 분리. Day 1부터 2-service 배포. PR 1 task 12→16개, 총 48→52.
- **프론트엔드(Next.js) 판단 보류** (2026-08-08). 사용자 편의성·협업능력 어필 관점에서 재검토했으나 PR 1~5 완료 후 시간·필요성 재평가하기로. 현재 계획서 §12 결정(프론트 X) 유지, 대신 OpenAPI 문서/결정 로그/벤치마크로 협업능력·진정성 신호 대체.
- **T1.3 스코프 축소: Anthropic 제외, OpenAI(gpt-4o-mini)만** (2026-08-08). Day 1 스코프 최소화. 필요시 model_list에 추가만 하면 되므로 확장 비용 저렴. `LITELLM_MASTER_KEY=sk-1234` (LiteLLM 커뮤니티 표준 dev 기본값).
- **T1.10 트러블슈팅 3건** (2026-08-09):
  1. **LiteLLM `/health`가 master_key 인증 요구** → K8s probe가 401 → CrashLoopBackOff. 해결: `/health/liveliness`, `/health/readiness` (인증 없는 별도 엔드포인트)로 변경.
  2. **shell `$OPENAI_API_KEY` 미로드 상태에서 helm upgrade** → Secret에 빈값 → OpenAI 401. 해결: `set -a; source .env; set +a`로 재로드 후 helm upgrade.
  3. **OpenAI 크레딧 소진** → 429 RateLimitError. 해결: billing 페이지에서 충전.

---

## 하드 제약

- **가용 시간 1주 미만.** 이동 중 노트북 작업. 안정적 GPU 없음.
- K8s는 **`kind`로 노트북 안에서 완결.** EKS/GKE 아님.
- vLLM은 **CPU + 초소형 모델** (`Qwen/Qwen2.5-0.5B-Instruct`).
- **Day 1만 끝나도 뱅크 K8s 필수요건은 확보** — 뒤 Day는 우대 가산점. 스코프 초과보다 Day 1 완주가 우선.

## 스코프 가드레일 (하지 말 것)

- **프론트엔드 (Next.js 등) 만들지 마.** "UI"는 Grafana 대시보드 + 아키텍처 다이어그램 + README. Streamlit/Gradio도 Day 5 옵션일 뿐.
- **PII 탐지 고도화하지 마.** 한국어 정규식(계좌·주민·카드·전화) + 옵션 Presidio면 충분. 정확도 튜닝은 스코프 밖.
- **없는 요구사항 만들지 마.** 계획서에 없는 기능·추상화·리팩토링 금지. 3줄 중복이 섣부른 추상화보다 낫다.

## 백업안 (막히면 즉시 전환)

vLLM CPU 이미지 빌드가 무겁고 컴파일이 이동 중 네트워크/사양에서 막힐 수 있음. **정공법 시도 → 막히면 Colab 무료 GPU(T4)에 vLLM 띄우고 `kind`의 게이트웨이가 `cloudflared`/`ngrok` 터널로 그걸 라우팅.** K8s 필수는 게이트웨이 배포로 이미 충족이라 OK.

## 재활용 자산 (새로 만들지 말 것)

지원자가 이미 가진 자산 — 재발명 금지, 이 위에 얹기:
- LiteLLM Proxy 기반 멀티 LLM 라우팅
- 클라이언트별 비용추적 (TokenCollector)
- BYOK 인증 구조, JWT
- LangGraph 에이전트 (SQL 의도분류 노드 → PII 분류 라우팅으로 연장)

## 브랜치 정책

- `main` — 배포 가능한 상태만
- `develop` — 통합 브랜치, 여기서 작업 브랜치 파생
- `feature/*` — 기능 단위 작업
- 원격 push는 명시적으로 요청받았을 때만 (로컬 우선)
- GitHub branch protection은 아직 안 걸림 (개발 우선)

## 슬래시 커맨드

- `/new-branch [name]` — `origin/main` 최신 기준으로 로컬 브랜치 생성 + checkout. 인자 없으면 `develop`. push 안 함.

## 커밋 컨벤션 — Conventional Commits

**포맷:** `<type>(<scope>): <subject>`

**Type:**
- `feat` — 새 기능 (사용자에게 보이는 변화)
- `fix` — 버그 수정
- `chore` — 빌드·설정·툴링 (동작 변화 없음)
- `docs` — 문서만 변경
- `refactor` — 리팩토링 (동작 변화 없음)
- `test` — 테스트 추가·수정
- `style` — 포맷·공백만

**Scope (선택):** `api`, `litellm`, `vllm`, `helm`, `k8s`, `ci`, `deps` 등

**Body (선택):** what/why/tradeoff 짧게. 왜 이렇게 했는지 결정 근거 담기.

**예시:**
```
feat(api): add PII detection middleware

한국어 정규식(계좌·주민·카드·전화) 기반 감지 → 마스킹 → LiteLLM으로 forward.
Presidio 대신 정규식 채택: 데모 스코프에 충분, 설치 리스크 회피.
```

**규칙:**
- subject는 명령형·소문자·마침표 없이 (`add`, `update`, `fix` — `added`/`Adds` X)
- 하나의 커밋 = 하나의 관심사 (섞지 말 것)
- 스코프 확실할 때만 붙임 (여러 파트 걸치면 생략)
