#!/usr/bin/env bash
# Smoke test for LiteLLM gateway (T1.10)
# Verifies: Ingress → Service → LiteLLM → OpenAI end-to-end
set -euo pipefail

URL="http://gateway.localtest.me/v1/chat/completions"
MASTER_KEY="${LITELLM_MASTER_KEY:-sk-1234}"

echo "→ POST ${URL}"
curl -sS -X POST "${URL}" \
  -H "Authorization: Bearer ${MASTER_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Say hi in one word"}]}' \
  | tee /dev/stderr | jq -e '.choices[0].message.content' >/dev/null 2>&1 \
  && echo -e "\n✅ SUCCESS — OpenAI 응답 정상" \
  || { echo -e "\n❌ FAILED — 응답 파싱 실패 (위 응답 확인)"; exit 1; }
