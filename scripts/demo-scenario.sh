#!/usr/bin/env bash
# Hybrid routing demo (T3.7)
# A: PII request  → routed to on-prem vLLM (vllm-qwen)
# B: General FAQ  → routed to commercial OpenAI (gpt-4o-mini)
#
# Verifies via the `model` field of the response (LiteLLM echoes actual served model).
set -euo pipefail

URL="http://api.localtest.me/v1/chat/completions"

run_scenario() {
  local label="$1"
  local user_msg="$2"
  local expected_model="$3"

  echo "──────────────────────────────────────────────────────────"
  echo "▶ $label"
  echo "  요청: $user_msg"
  echo "  기대 라우팅: $expected_model"

  local body
  body=$(jq -nc --arg m "$user_msg" '{
    model: "will-be-overridden-by-fastapi-router",
    messages: [{role: "user", content: $m}],
    max_tokens: 40
  }')

  local resp
  resp=$(curl -sS -X POST "$URL" -H 'Content-Type: application/json' -d "$body")

  local actual_model
  actual_model=$(echo "$resp" | jq -r '.model // "MISSING"')

  local content
  content=$(echo "$resp" | jq -r '.choices[0].message.content // .error.message // "MISSING"')

  echo "  실제 라우팅: $actual_model"
  echo "  응답: $content"

  # tolerant match (LiteLLM/OpenAI may append suffixes like gpt-4o-mini-2024-...)
  if [[ "$actual_model" == "$expected_model"* ]] || [[ "$actual_model" == *"$expected_model"* ]]; then
    echo "  ✅ 라우팅 일치"
  else
    echo "  ❌ 라우팅 불일치 (expected: $expected_model, actual: $actual_model)"
  fi
  echo ""
}

echo "═══════════════════════════════════════════════════════════"
echo "  Hybrid LLM Gateway — Routing Demo"
echo "═══════════════════════════════════════════════════════════"
echo ""

# A: PII 포함 요청 → vLLM (온프레)
run_scenario \
  "Scenario A: PII 요청 (계좌번호 포함)" \
  "제 계좌 123-456-789로 오늘 이체된 내역 조회해줘" \
  "vllm-qwen"

# B: 일반 FAQ → 상용 API
run_scenario \
  "Scenario B: 일반 FAQ (PII 없음)" \
  "예금 상품 종류를 간단히 알려주세요" \
  "gpt-4o-mini"

echo "═══════════════════════════════════════════════════════════"
echo "  로그로 라우팅 흔적 확인:"
echo "    kubectl logs -n pii deployment/gateway-api --tail=20"
echo "    kubectl logs -n pii deployment/gateway-litellm --tail=20"
echo "═══════════════════════════════════════════════════════════"
