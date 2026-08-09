#!/usr/bin/env bash
# End-to-end smoke test for the full gateway (T1.16)
# Verifies: Ingress → FastAPI → LiteLLM → OpenAI (4-hop)
set -euo pipefail

URL="http://api.localtest.me/v1/chat/completions"

echo "→ POST ${URL}"
curl -sS -X POST "${URL}" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Say hi in one word"}]}' \
  | tee /dev/stderr | jq -e '.choices[0].message.content' >/dev/null 2>&1 \
  && echo -e "\n✅ SUCCESS — 4-hop 정상 (Ingress → FastAPI → LiteLLM → OpenAI)" \
  || { echo -e "\n❌ FAILED — 응답 파싱 실패 (위 응답 확인)"; exit 1; }
