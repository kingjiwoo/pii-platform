SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help

NAMESPACE     ?= pii
KIND_CLUSTER  ?= pii-platform
IMAGE_TAG     ?= dev

# ==========================================
##@ Meta
# ==========================================

.PHONY: help
help: ## 사용 가능한 명령 목록
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

# ==========================================
##@ Cluster
# ==========================================

.PHONY: kind-up
kind-up: ## kind 클러스터 생성
	kind create cluster --name $(KIND_CLUSTER) --config deploy/kind/kind-config.yaml

.PHONY: kind-down
kind-down: ## kind 클러스터 삭제
	kind delete cluster --name $(KIND_CLUSTER)

.PHONY: ingress-install
ingress-install: ## ingress-nginx 설치 (kind용)
	kubectl apply -f https://kind.sigs.k8s.io/examples/ingress/deploy-ingress-nginx.yaml
	kubectl wait --namespace ingress-nginx --for=condition=ready pod \
	  --selector=app.kubernetes.io/component=controller --timeout=180s

.PHONY: up
up: kind-up ingress-install ## 클러스터 + ingress (처음 시작)

.PHONY: down
down: kind-down ## 클러스터 통째로 삭제

# ==========================================
##@ Build (Docker)
# ==========================================

.PHONY: build-api
build-api: ## FastAPI 이미지 빌드
	docker build -t pii-api:$(IMAGE_TAG) -f docker/api/Dockerfile .

.PHONY: build-litellm
build-litellm: ## LiteLLM 이미지 빌드
	docker build -t pii-litellm:$(IMAGE_TAG) docker/litellm

.PHONY: build-vllm
build-vllm: ## vLLM 이미지 빌드 (PR 2)
	docker build -t pii-vllm:$(IMAGE_TAG) docker/vllm

.PHONY: build
build: build-api build-litellm ## FastAPI + LiteLLM 이미지 빌드

# ==========================================
##@ Load (kind로 이미지 로드)
# ==========================================

.PHONY: load-api
load-api: ## FastAPI 이미지 kind로 로드
	kind load docker-image pii-api:$(IMAGE_TAG) --name $(KIND_CLUSTER)

.PHONY: load-litellm
load-litellm: ## LiteLLM 이미지 kind로 로드
	kind load docker-image pii-litellm:$(IMAGE_TAG) --name $(KIND_CLUSTER)

.PHONY: load-vllm
load-vllm: ## vLLM 이미지 kind로 로드
	kind load docker-image pii-vllm:$(IMAGE_TAG) --name $(KIND_CLUSTER)

.PHONY: load
load: load-api load-litellm ## 모든 이미지 로드

# ==========================================
##@ Deploy (Helm)
# ==========================================

.PHONY: ns
ns: ## 네임스페이스 생성 (idempotent)
	kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -

.PHONY: install-api
install-api: ns ## FastAPI Helm install/upgrade
	helm upgrade --install api deploy/helm/api -n $(NAMESPACE) --set image.tag=$(IMAGE_TAG)

.PHONY: install-litellm
install-litellm: ns ## LiteLLM Helm install/upgrade
	helm upgrade --install litellm deploy/helm/litellm -n $(NAMESPACE) --set image.tag=$(IMAGE_TAG)

.PHONY: install-vllm
install-vllm: ns ## vLLM Helm install/upgrade (PR 2)
	helm upgrade --install vllm deploy/helm/vllm -n $(NAMESPACE)

.PHONY: install
install: install-litellm install-api ## 모든 서비스 install (LiteLLM 먼저)

.PHONY: uninstall
uninstall: ## 모든 서비스 uninstall
	-helm uninstall api -n $(NAMESPACE)
	-helm uninstall litellm -n $(NAMESPACE)
	-helm uninstall vllm -n $(NAMESPACE)

.PHONY: deploy
deploy: build load install ## build + load + install (원샷)

# ==========================================
##@ Debug / Ops
# ==========================================

.PHONY: pf
pf: ## FastAPI 로컬 8000 포트로 forward
	kubectl port-forward -n $(NAMESPACE) svc/api 8000:8000

.PHONY: logs-api
logs-api: ## FastAPI 로그 tail
	kubectl logs -f -n $(NAMESPACE) -l app.kubernetes.io/name=api

.PHONY: logs-litellm
logs-litellm: ## LiteLLM 로그 tail
	kubectl logs -f -n $(NAMESPACE) -l app.kubernetes.io/name=litellm

.PHONY: logs-vllm
logs-vllm: ## vLLM 로그 tail
	kubectl logs -f -n $(NAMESPACE) -l app.kubernetes.io/name=vllm

.PHONY: status
status: ## 클러스터 리소스 상태
	kubectl get pods,svc,ingress,hpa -n $(NAMESPACE)

.PHONY: smoke
smoke: ## 스모크 테스트 실행
	bash scripts/smoke-api.sh
