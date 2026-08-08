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

**전체:** `5 / 52` task 완료 (10%)

| PR | 브랜치 | Task | 상태 |
|----|--------|------|------|
| PR 0 | `feat/settings` (원래 계획: chore/initial-setup) | 5/8 | ⏳ 진행중 |
| PR 1 ⭐ | `feat/day1-fastapi-litellm-on-kind` | 0/16 | 🔒 잠김 (PR 0 후) |
| PR 2 | `feat/day2-vllm-on-k8s` | 0/7 | 🔒 잠김 |
| PR 3 | `feat/day3-sensitivity-routing` | 0/8 | 🔒 잠김 |
| PR 4 | `feat/day4-observability` | 0/6 | 🔒 잠김 |
| PR 5 | `feat/day5-ops-polish` | 0/7 | 🔒 잠김 |

**현재 위치:** PR 0 진행중. 다음 할 일 = **T0.6** (`docs/architecture.svg` 옵시디언에서 복사).

**마일스톤:**
- 🎯 **PR 1 완료** = 뱅크 K8s 필수요건 충족 (최우선)
- 🎯 **PR 3 완료** = 도메인 스토리(하이브리드 라우팅) 완성
- 🎯 **PR 5 완료** = 포트폴리오 완성

### 진행중 task (있으면)

_없음_

### 최근 완료 (최대 5개)

- ✅ T0.5 — `Makefile` 뼈대 (help/kind/build/load/install/uninstall/deploy/pf/logs/smoke, `##@` 섹션 헤더 + `##` 자동 도움말)
- ✅ T0.4 — `.env.example` (OPENAI/ANTHROPIC/LITELLM_MASTER_KEY 플레이스홀더) + `.editorconfig` (YAML 2sp, Python 4sp, Makefile tab, LF)
- ✅ T0.3 — 디렉토리 스켈레톤 (deploy/{kind,helm/{api,litellm,vllm,monitoring},monitoring,grafana}, docker/{api,litellm,vllm}, src/api, scripts, docs)
- ✅ T0.2 — `.gitignore` 작성 (Python, K8s, secrets, IDE, OS)
- ✅ T0.1 — 초기 세팅 브랜치 확보 (`feat/settings`로 대체, 이름만 다르고 역할 동일)

### 결정·트러블 로그

- 브랜치명 `feat/settings` 유지 (계획서는 `chore/initial-setup`). 이름보다 진도 우선.
- `/new-branch` 슬래시 커맨드 재생성 스킵 — 사용자가 브랜치 직접 만들기로 함.
- **아키텍처 변경: FastAPI 서비스 레이어 추가** (2026-08-08). PII·auth·라우팅 결정 = FastAPI, LLM 어댑터 = LiteLLM으로 계층 분리. Day 1부터 2-service 배포. PR 1 task 12→16개, 총 48→52.

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

## 커밋 컨벤션

아직 미정. 첫 커밋 만들 때 결정 후 여기 기록.
