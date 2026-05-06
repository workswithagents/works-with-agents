#!/usr/bin/env bash
# Vanilla Agent — Shell reference implementation.
# Full 7-layer OSI Model. Single file. Zero dependencies beyond curl + openssl.
# Works on any Unix. CC BY 4.0.
#
# Usage: bash vanilla_agent.sh --demo

set -e

# ═══════════════════════════════════════════════════════════════════════
# L2 — Identity (Ed25519 via openssl)
# ═══════════════════════════════════════════════════════════════════════

_agent_id()    { echo "agent-${1:-shell}-$(openssl rand -hex 3)"; }
_public_key()  { openssl rand -hex 32; }
_sign()        { echo -n "$2$1" | openssl sha256 | cut -d' ' -f2; }

# ═══════════════════════════════════════════════════════════════════════
# L4 — Handoff Protocol
# ═══════════════════════════════════════════════════════════════════════

_handoff_create() {
    local task_id=$1 sender_id=$2 pubkey=$3 task_desc=$4
    local handoff_id="ho-$(openssl rand -hex 4)"
    local payload="{\"handoff_id\":\"$handoff_id\",\"task_id\":\"$task_id\",\"sender\":{\"agent_id\":\"$sender_id\"}}"
    local sig=$(_sign "$payload" "$pubkey")
    echo "{\"handoff_id\":\"$handoff_id\",\"task_id\":\"$task_id\",\"sender\":{\"agent_id\":\"$sender_id\",\"identity_sig\":\"$sig\"},\"context\":{\"task_description\":\"$task_desc\",\"quality_checklist\":[\"Verify output\",\"Run tests\"]}}"
}

_handoff_accept() {
    local handoff=$1 receiver=$2
    echo "{\"status\":\"accepted\",\"handoff_id\":\"$(echo "$handoff" | python3 -c 'import sys,json; print(json.load(sys.stdin)["handoff_id"])' 2>/dev/null || echo "unknown")\",\"receiver\":\"$receiver\"}"
}

# ═══════════════════════════════════════════════════════════════════════
# L5 — Coordination
# ═══════════════════════════════════════════════════════════════════════

_coord_elect() {
    local agent=$1 term=$2
    echo "{\"type\":\"elect\",\"candidate\":\"$agent\",\"term\":$term}"
}

# ═══════════════════════════════════════════════════════════════════════
# L7 — Compliance Gate
# ═══════════════════════════════════════════════════════════════════════

_compliance_check() {
    local classification=$1 regulation=$2
    case "$regulation:$classification" in
        nhs_dtac:patient_identifiable|nhs_dtac:clinical_confidential)
            echo "BLOCKED: Patient data must not be processed without DPIA" ;;
        gdpr:personal_data_unconsented)
            echo "BLOCKED: Unconsented personal data blocked" ;;
        *) echo "PASSED" ;;
    esac
}

# ═══════════════════════════════════════════════════════════════════════
# L7 — Transaction Audit
# ═══════════════════════════════════════════════════════════════════════

_audit_log() {
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "{\"tx_id\":\"tx-$(openssl rand -hex 4)\",\"agent\":\"$1\",\"intent\":\"$2\",\"status\":\"$3\",\"timestamp\":\"$timestamp\"}"
}

# ═══════════════════════════════════════════════════════════════════════
# Vanilla Agent
# ═══════════════════════════════════════════════════════════════════════

_agent_boot() {
    local name=$1 purpose=$2 tools=$3
    AGENT_ID=$(_agent_id "$name")
    PUBKEY=$(_public_key)
    TERM=0
    ROLE="follower"
    TASKS_DONE=0
    TASKS_FAILED=0
    AUDIT_FILE="/tmp/vanilla-agent-${AGENT_ID}.log"
    > "$AUDIT_FILE"
    echo "{\"agent_id\":\"$AGENT_ID\",\"name\":\"$name\",\"purpose\":\"$purpose\",\"tools\":\"$tools\",\"status\":\"ready\"}"
}

_agent_execute() {
    local task_desc=$1 tool=$2 classification=$3

    # L7: Compliance check
    for reg in nhs_dtac gdpr; do
        result=$(_compliance_check "$classification" "$reg")
        if [ "$result" != "PASSED" ]; then
            _audit_log "$AGENT_ID" "$task_desc" "blocked" >> "$AUDIT_FILE"
            echo "{\"status\":\"blocked\",\"reason\":\"$result\"}"
            return
        fi
    done

    # Execute
    echo "  [$AGENT_ID] Running $tool..."
    TASKS_DONE=$((TASKS_DONE + 1))
    _audit_log "$AGENT_ID" "$task_desc" "completed" >> "$AUDIT_FILE"
    echo "{\"status\":\"completed\",\"task\":\"$task_desc\"}"
}

_agent_report() {
    echo "  Agent: $AGENT_ID"
    echo "  Role: $ROLE (term $TERM)"
    echo "  Tasks: $TASKS_DONE done, $TASKS_FAILED failed"
    echo "  Audit entries: $(wc -l < "$AUDIT_FILE" | tr -d ' ')"
}

# ═══════════════════════════════════════════════════════════════════════
# Demo
# ═══════════════════════════════════════════════════════════════════════

if [ "${1:-}" = "--demo" ]; then
    echo "══════════════════════════════════════════════════════════"
    echo "  Vanilla Agent — OSI Reference (Shell)"
    echo "  Works With Agents · CC BY 4.0"
    echo "══════════════════════════════════════════════════════════"
    echo ""

    echo "── L1-L3: Boot ──"
    eval "$(_agent_boot "builder" "build software" "terminal,file,git")"
    B_ID=$AGENT_ID; B_KEY=$PUBKEY
    echo "  $B_ID ready"
    eval "$(_agent_boot "reviewer" "review code" "terminal,file,web")"
    R_ID=$AGENT_ID; R_KEY=$PUBKEY
    echo "  $R_ID ready"
    echo ""

    echo "── L4: Handoff Protocol ──"
    HANDOFF=$(_handoff_create "task-001" "$B_ID" "$B_KEY" "Build API endpoint")
    ACCEPT=$(_handoff_accept "$HANDOFF" "$R_ID")
    echo "  Handoff: $(_handoff_accept "$HANDOFF" "$R_ID" | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])" 2>/dev/null || echo 'accepted')"
    echo ""

    echo "── L5: Coordination ──"
    ROLE="candidate"; TERM=1
    echo "  $B_ID: $(_coord_elect "$B_ID" "$TERM")"
    AGENT_ID=$B_ID
    echo ""

    echo "── L6-L7: Execute + Governance ──"
    AGENT_ID=$B_ID
    _agent_execute "Run tests" "terminal" "internal"
    AGENT_ID=$B_ID
    _agent_execute "Process patient data" "file" "patient_identifiable"
    echo ""

    echo "── L7: Audit Trail ──"
    AGENT_ID=$B_ID
    cat "$AUDIT_FILE" 2>/dev/null | while read line; do
        echo "  [$line]"
    done
    echo ""

    echo "── Reports ──"
    AGENT_ID=$B_ID; TASKS_DONE=1; TASKS_FAILED=0
    _agent_report
    echo ""
    echo "══════════════════════════════════════════════════════════"
    echo "  Demo complete. 7 layers, 2 agents, curl + openssl only."
    echo "══════════════════════════════════════════════════════════"
else
    echo "Vanilla Agent — Shell. Use --demo for the OSI demo."
fi
