#!/usr/bin/env bash
# T5.4 — Helm rollback demo for gateway-api chart.
# Rolls back to the immediately previous revision (or a specified one).
#
# Usage:
#   ./scripts/rollback-demo.sh                  # roll back to previous revision
#   ./scripts/rollback-demo.sh 3                # roll back to revision 3
set -euo pipefail

REL=${REL:-gateway-api}
NS=${NS:-pii}
TARGET_REV=${1:-}

echo "──────────────────────────────────────────────"
echo "  Helm rollback demo — release=$REL, ns=$NS"
echo "──────────────────────────────────────────────"

echo ""
echo "▶ Before: helm history"
helm history "$REL" -n "$NS"

echo ""
echo "▶ Before: current image tag"
kubectl get deployment "$REL" -n "$NS" -o jsonpath='{.spec.template.spec.containers[0].image}'
echo ""

echo ""
if [ -z "$TARGET_REV" ]; then
  echo "▶ Rolling back to previous revision..."
  helm rollback "$REL" -n "$NS"
else
  echo "▶ Rolling back to revision $TARGET_REV..."
  helm rollback "$REL" "$TARGET_REV" -n "$NS"
fi

echo ""
echo "▶ Waiting for rollout to finish..."
kubectl rollout status "deployment/$REL" -n "$NS"

echo ""
echo "▶ After: current image tag"
kubectl get deployment "$REL" -n "$NS" -o jsonpath='{.spec.template.spec.containers[0].image}'
echo ""

echo ""
echo "▶ After: helm history (new entry appended)"
helm history "$REL" -n "$NS"

echo ""
echo "✅ Rollback complete. Deployment now serving the previous version."
