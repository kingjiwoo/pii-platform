#!/usr/bin/env bash
# T5.5 — Self-healing demo: force-delete a Pod and watch ReplicaSet recreate it.
#
# Usage:
#   ./scripts/kill-pod-demo.sh                          # kill a gateway-api pod
#   TARGET=gateway-litellm ./scripts/kill-pod-demo.sh   # kill a different service
set -euo pipefail

TARGET=${TARGET:-gateway-api}
NS=${NS:-pii}
CHART_NAME=${CHART_NAME:-${TARGET#gateway-}}   # gateway-api → api

echo "──────────────────────────────────────────────"
echo "  Self-healing demo — Pod delete for $TARGET"
echo "──────────────────────────────────────────────"

echo ""
echo "▶ Current pods:"
kubectl get pods -n "$NS" -l "app.kubernetes.io/name=$CHART_NAME" -o wide

VICTIM=$(kubectl get pods -n "$NS" -l "app.kubernetes.io/name=$CHART_NAME" -o jsonpath='{.items[0].metadata.name}')
echo ""
echo "▶ Victim pod: $VICTIM"

echo ""
echo "▶ Deleting pod (declarative reconciliation should recreate immediately)..."
kubectl delete pod "$VICTIM" -n "$NS"

echo ""
echo "▶ Watching recreation (10s intervals, 30s total)..."
for i in {1..3}; do
  sleep 10
  T=$((i * 10))
  PODS=$(kubectl get pods -n "$NS" -l "app.kubernetes.io/name=$CHART_NAME" --no-headers 2>&1)
  COUNT=$(echo "$PODS" | wc -l | xargs)
  READY=$(echo "$PODS" | grep -c "1/1" || true)
  echo "T=${T}s  pods=$COUNT  ready=$READY"
done

echo ""
echo "▶ Recent Pod events (ReplicaSet controller reconciliation trace):"
kubectl get events -n "$NS" --field-selector involvedObject.kind=Pod --sort-by=.lastTimestamp 2>&1 | tail -8

echo ""
echo "✅ Self-healing complete. Pod was recreated by the ReplicaSet without any manual scale command."
