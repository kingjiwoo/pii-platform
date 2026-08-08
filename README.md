# pii-platform

**Compliance-aware hybrid LLM gateway on Kubernetes** — routes PII requests to a self-hosted vLLM backend and general traffic to commercial APIs, with cost & SLA observability.

> Route by data sensitivity, not by guesswork. Keep customer PII on-prem, send the rest to the best commercial model — all on Kubernetes.

---

## 문제 정의

금융권은 고객 PII·거래정보를 외부 LLM API로 못 보낸다 (컴플라이언스). 그렇다고 상용 API 품질도 포기 못 한다.

→ **민감도를 판별해 PII 요청은 사내 vLLM(온프레)으로, 일반 요청은 상용 API로 보내는 하이브리드 LLM 게이트웨이를 Kubernetes 위에 구축**하고 비용·SLA를 관측한다.

## 아키텍처

```
[Client / 데모 스크립트]
        │
        ▼
┌─────────────────────────────┐
│  LiteLLM Gateway (K8s)      │
│  - 민감도 판별 (PII 탐지)    │
│  - 라우팅 결정              │
│  - BYOK/인증, 비용 기록      │
└───────┬─────────────┬───────┘
        │ PII 있음     │ PII 없음
        ▼             ▼
┌──────────────┐   ┌──────────────────┐
│ vLLM (K8s,    │   │ 상용 API          │
│ CPU, 소형모델)│   │ (OpenAI/Anthropic)│
│ = 온프레 처리 │   │ = 고품질 처리     │
└──────────────┘   └──────────────────┘
        │
        ▼
[Prometheus / Grafana]
  · 민감 vs 비민감 트래픽 비율
  · 클라이언트별 토큰 비용
  · p50 / p95 / p99 latency, 에러율
  · vLLM KV캐시 사용률·throughput
```

## 기술 스택 & 도메인 정당성

| 기술 | 왜 있는가 |
|---|---|
| LiteLLM 게이트웨이 | 민감도 기반 **라우팅 두뇌** |
| **vLLM on K8s (CPU, 소형 모델)** | 민감정보를 **밖으로 안 보내고** 처리하는 온프레 백엔드 |
| PII 탐지 노드 | 라우팅 **결정 로직** (한국어 정규식 + 옵션: Presidio) |
| BYOK / JWT 인증 | 팀·클라이언트별 접근 통제 |
| Prometheus / Grafana | **SLA·비용** 관측, 민감/비민감 트래픽 분리 |
| Kubernetes + HPA | 운영·스케일·self-healing |

**주요 스택:** `kind`, `Helm`, `kubectl`, LiteLLM, vLLM (CPU), FastAPI, Prometheus, Grafana (kube-prometheus-stack), Docker

## 데모 시나리오

"고객 상담 문의 처리"

- 계좌번호/주민번호가 든 문의 → **온프레 vLLM** 처리 (+ PII 마스킹)
- 일반 FAQ 문의 → **상용 API** 처리
- Grafana에서 **민감 vs 비민감 트래픽 비율·비용·latency를 한 화면**에 시각화

## 로드맵

| Day | 목표 | 산출물 |
|-----|------|--------|
| 1 | K8s 필수 확보 ⭐ (게이트웨이 배포) | kind 클러스터 + Helm 차트로 도는 LiteLLM |
| 2 | vLLM을 K8s에 배포 (온프레 백엔드) | CPU 모드 vLLM Deployment + Service |
| 3 | 민감도 라우팅 (도메인 핵심) | PII 감지 → vLLM / 미감지 → 상용 API |
| 4 | 관측성 (SLA·비용) | Grafana 대시보드 |
| 5 | 운영 티 + 문서화 | HPA, 롤백 시연, 아키텍처 다이어그램 |

> Day 1만 끝나도 K8s 필수요건은 확보. 뒤 날짜는 전부 우대 가산점 → 시간 밀려도 손해 최소.

## 스코프 & 트레이드오프

- **PII 탐지는 정규식 수준의 데모** — 핵심은 탐지 정확도가 아니라 "민감도로 라우팅을 가르는 아키텍처"
- **프론트엔드 없음** — 이 프로젝트의 "UI"는 Grafana 대시보드 + 아키텍처 다이어그램. LLM Ops 포지션은 백엔드·인프라를 봄
- **vLLM CPU 백업안** — CPU 이미지 빌드가 막히면 Colab GPU + `cloudflared` 터널로 전환. K8s 필수는 게이트웨이 배포로 이미 충족되어 있어 OK

## 상태

- [x] 계획 완료
- [ ] Day 1 — 게이트웨이 K8s 배포
- [ ] Day 2 — vLLM 배포
- [ ] Day 3 — 라우팅
- [ ] Day 4 — 관측성
- [ ] Day 5 — 운영·문서화
