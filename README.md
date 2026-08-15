# pii-platform

**Compliance-aware hybrid LLM gateway on Kubernetes** — routes PII requests to a self-hosted vLLM backend and general traffic to commercial APIs, with cost & SLA observability.

> Route by data sensitivity, not by guesswork. Keep customer PII on-prem, send the rest to the best commercial model — all on Kubernetes.

---

## 문제 정의

금융권은 고객 PII·거래정보를 외부 LLM API로 못 보낸다 (컴플라이언스). 그렇다고 상용 API 품질도 포기 못 한다.

→ **민감도를 판별해 PII 요청은 사내 vLLM(온프레)으로, 일반 요청은 상용 API로 보내는 하이브리드 LLM 게이트웨이를 Kubernetes 위에 구축**하고 비용·SLA를 관측한다.

## 아키텍처

```
[Client]  →  Ingress (api.localtest.me)
                  │
                  ▼
      ┌────────────────────────────────┐
      │  FastAPI (K8s Deployment)       │  ← 진입점 / 도메인 로직
      │  · PII 감지 (Detector Protocol) │
      │  · 마스킹 (Masker Protocol)     │
      │  · 라우팅 판단 (Router Protocol)│
      │  · Prometheus 커스텀 메트릭     │
      └────────────────┬───────────────┘
                       │ in-cluster: model_name 명시
                       ▼
      ┌────────────────────────────────┐
      │  LiteLLM Proxy (K8s Deployment) │  ← LLM 어댑터 (OpenAI 호환)
      │  · model → 백엔드 매핑            │
      │  · master_key 인증               │
      └───────┬──────────────────┬─────┘
              │ vllm-qwen         │ gpt-4o-mini
              ▼                   ▼
      ┌──────────────┐    ┌──────────────┐
      │ vLLM (K8s)    │    │ OpenAI API   │
      │ Qwen2.5-0.5B  │    │ (상용)        │
      │ 온프레 처리   │    │              │
      └──────────────┘    └──────────────┘
              │
              ▼
      [Prometheus + Grafana]
        · PII vs Non-PII 라우팅 비율
        · 모델별 요청 수
        · p50 / p95 / p99 latency
        · vLLM active requests · tokens/sec

      [HPA (custom metric)]
        · http_requests_per_second 기반 자동 스케일 (min 1, max 5)
```

> **계층 분리:** FastAPI가 도메인 로직 (PII·auth·라우팅 결정), LiteLLM은 순수 LLM 어댑터. 관심사 분리로 각 계층의 확장 자유 확보.

## 기술 스택

| 계층 | 컴포넌트 | 역할 |
|---|---|---|
| **진입점** | FastAPI + Ingress-nginx | HTTP 파싱, 도메인 로직 (PII·라우팅), 커스텀 메트릭 노출 |
| **어댑터** | LiteLLM Proxy | OpenAI 호환 스펙으로 여러 백엔드 통합 (retry, cost tracking 기본 제공) |
| **온프레 백엔드** | vLLM (CPU, `Qwen2.5-0.5B-Instruct`) | 민감정보 외부 유출 없이 처리 |
| **상용 백엔드** | OpenAI `gpt-4o-mini` | 일반 요청용 고품질 응답 |
| **오케스트레이션** | Kubernetes (kind) + Helm | 선언적 배포, 롤아웃/롤백, self-healing |
| **관측성** | kube-prometheus-stack + prometheus-adapter | 메트릭·대시보드·custom metric HPA |


## 데모 시나리오

"고객 상담 문의 처리"

- 계좌번호/주민번호가 든 문의 → **온프레 vLLM** 처리 (+ PII 마스킹)
- 일반 FAQ 문의 → **상용 API** 처리
- Grafana에서 **민감 vs 비민감 트래픽 비율·비용·latency를 한 화면**에 시각화

## 로드맵

| Day | 목표 | 산출물 |
|-----|------|--------|
| 1 | 게이트웨이 K8s 배포 | kind 클러스터 + Helm 차트로 도는 FastAPI + LiteLLM |
| 2 | vLLM 온프레 백엔드 배포 | CPU 모드 vLLM Deployment + Service |
| 3 | 민감도 기반 라우팅 (도메인 핵심) | PII 감지 → vLLM / 미감지 → 상용 API |
| 4 | 관측성 스택 | Prometheus + Grafana 대시보드 |
| 5 | 운영 시나리오 시연 | HPA (custom metric), 롤아웃/롤백, self-healing |

## 스코프 & 트레이드오프

- **PII 탐지는 정규식 수준의 데모** — 핵심은 탐지 정확도가 아니라 "민감도로 라우팅을 가르는 아키텍처". 프로덕션에서는 사내 DLP 또는 Presidio 연동으로 대체 가능하도록 `Detector` Protocol 뒤에 격리
- **프론트엔드 없음** — 이 프로젝트의 UI는 Grafana 대시보드 + 아키텍처 다이어그램. 프로젝트 관심사는 백엔드·인프라 계층
- **CPU 서빙** — kind에서 vLLM CPU 모드로 실행. 프로덕션은 GPU 노드 필수 (튜닝 파라미터·리소스는 그대로 재사용, `values.yaml`의 image tag만 GPU 이미지로 교체)

## 상태

- [x] 계획 완료
- [x] **Day 1 — 게이트웨이 K8s 배포** ✅ (PR #2 머지, 2026-08-09) → [빠른 시작](#빠른-시작)
- [x] **Day 2 — vLLM 배포** ✅ (PR #3 머지, 2026-08-12) — CPU 모드로 Qwen2.5-0.5B-Instruct 서빙
- [x] **Day 3 — 하이브리드 라우팅** ✅ (PR #4 머지, 2026-08-13) — PII → 온프레 vLLM, 일반 → OpenAI
- [x] **Day 4 — 관측성** ✅ (PR #5 머지, 2026-08-14) → [대시보드](#관측성-grafana-대시보드)
- [x] **Day 5 — 운영 시나리오** ✅ (2026-08-16) → [운영 기능](#운영-hpa--롤아웃--self-healing)

## 관측성 (Grafana 대시보드)

`kube-prometheus-stack` + FastAPI 커스텀 메트릭(`pii_detections_total`, `routing_decisions_total`) + vLLM native 메트릭을 하나의 대시보드에 시각화. Dashboard-as-Code로 `deploy/grafana/hybrid-llm-dashboard.json`에 정의, ConfigMap sidecar로 Grafana에 자동 로드.

![Grafana — Hybrid LLM Gateway](docs/screenshots/grafana-hybrid-llm.png)

**핵심 패널:**

- **Routing rate — PII vs Non-PII** — `sum by (pii_detected) (rate(routing_decisions_total[5m]))` 스택드 뷰. 도메인 스토리 그 자체.
- **Routing decisions by target model** — vLLM vs OpenAI 누적 비율 (도넛)
- **PII detections by type** — 어떤 종류의 PII가 자주 감지되는지 (파이)
- **vLLM active requests / tokens/sec** — 온프레 백엔드 부하·처리량

접속:
```bash
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
# http://localhost:3000/d/hybrid-llm-gateway (admin / admin123)
```

## 운영 (HPA · 롤아웃 · Self-healing)

세 가지 K8s 운영 시나리오를 재사용 가능 스크립트로 시연.

### HPA (Custom Metric 기반)

CPU가 아닌 **요청 rate 기반** 스케일링 — I/O bound 워크로드에 맞는 신호. `prometheus-adapter`로 `http_requests_total`을 rate 계산해 `pods/http_requests_per_second` 라는 custom metric으로 K8s Metrics API에 노출, HPA v2가 이를 참조.

```yaml
autoscaling:
  minReplicas: 1
  maxReplicas: 5
  customMetrics:
    - type: Pods
      pods:
        metric: { name: http_requests_per_second }
        target: { type: AverageValue, averageValue: "2" }
```

**부하 시연 결과** (`hey -z 60s -c 20 -m GET http://api.localtest.me/health/liveliness`):
```
T=0s    REPLICAS=1  TARGETS=276m/2      (idle)
T=20s   REPLICAS=1  TARGETS=547671m/2   (부하 감지)
T=30s   REPLICAS=4  TARGETS=1846626m/2  (SCALE UP)
T=50s   REPLICAS=5  TARGETS=1375053m/2  (max 도달)
T=60s   부하 종료
T=180s  REPLICAS=5  TARGETS=264m/2      (metric 회복, 5분 stabilization 대기 중)
```

Scale-up 반응 시간 **20초**. Scale-down은 기본 5분 stabilization window로 보수적 처리.

### 롤링 업데이트 · 롤백

```bash
# 새 태그로 배포 (자동 rolling update)
helm upgrade gateway-api ./deploy/helm/api --set image.tag=dev-v2

# 문제 발생 시 즉시 롤백 (전용 스크립트)
./scripts/rollback-demo.sh
```

`helm rollback`은 **새 revision 엔트리를 추가**해 이전 상태로 복귀 (git revert 스타일, 히스토리 보존).

### Self-healing

```bash
./scripts/kill-pod-demo.sh
# → Pod 강제 삭제 → ReplicaSet 컨트롤러가 10초 내 재생성
```

Declarative 모델의 실증 — Pod을 죽여도 사람 개입 없이 자동 복구.

### 재사용 스크립트

| 스크립트 | 목적 |
|---|---|
| `scripts/smoke-api.sh` | E2E 스모크 (Ingress → FastAPI → LiteLLM → OpenAI) |
| `scripts/demo-scenario.sh` | 하이브리드 라우팅 데모 (PII vs 일반) |
| `scripts/rollback-demo.sh` | Helm rollback 시연 |
| `scripts/kill-pod-demo.sh` | Self-healing 시연 |
| `scripts/install-monitoring.sh` | kube-prometheus-stack 배포 |

## 빠른 시작

FastAPI + LiteLLM 2-service 하이브리드 게이트웨이를 로컬 kind 클러스터에 배포하고 스모크 테스트.

### 사전 요구

- macOS + Docker Desktop 실행 중
- `brew install kind kubectl helm`
- OpenAI API 키 ([발급](https://platform.openai.com/api-keys))

### 순서

```bash
# 1. 리포 세팅
git clone https://github.com/kingjiwoo/pii-platform && cd pii-platform
cp .env.example .env
# .env 파일 열어서 OPENAI_API_KEY=sk-... 채우기

# 2. kind 클러스터 생성
kind create cluster --config deploy/kind/kind-config.yaml

# 3. ingress-nginx Controller 설치
kubectl apply -f https://kind.sigs.k8s.io/examples/ingress/deploy-ingress-nginx.yaml
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s

# 4. 이미지 빌드 + kind 노드로 로드
docker build -t pii-litellm:dev docker/litellm/
docker build -f docker/api/Dockerfile -t pii-api:dev .
kind load docker-image pii-litellm:dev --name pii-platform
kind load docker-image pii-api:dev --name pii-platform

# 5. 환경변수 로드 후 Helm 배포
set -a; source .env; set +a

helm install gateway ./deploy/helm/litellm \
  --namespace pii --create-namespace \
  --set secrets.OPENAI_API_KEY=$OPENAI_API_KEY

helm install gateway-api ./deploy/helm/api --namespace pii

# 6. Pod Ready 대기
kubectl rollout status deployment/gateway-litellm -n pii
kubectl rollout status deployment/gateway-api -n pii

# 7. End-to-end 스모크 테스트 (Ingress → FastAPI → LiteLLM → OpenAI)
./scripts/smoke-api.sh
# → ✅ SUCCESS — 4-hop 정상
```

### 검증되는 것

- ✅ 2-service Helm chart 각각 배포 (Deployment/Service/ConfigMap/Secret/Ingress)
- ✅ `checksum/config` annotation으로 ConfigMap 변경 자동 반영
- ✅ 외부 진입점은 FastAPI 하나로 통일, LiteLLM은 내부 전용 (ClusterIP)
- ✅ Ingress-nginx가 host 기반 라우팅 (`api.localtest.me` → gateway-api Service)
