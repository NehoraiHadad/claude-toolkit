#!/bin/bash
# n8n Quick Actions
# Source this file to add n8n shortcuts to your shell
#
# Usage: source ~/.claude/skills/n8n-expert/scripts/quick-actions.sh
#
# Then use the shortcuts:
#   n8n-list       - List all workflows
#   n8n-active     - List active workflows
#   n8n-errors     - Show recent errors
#   n8n-trigger    - Trigger a webhook
#   n8n-exec       - List recent executions
#   n8n-health     - Check n8n health

# Configuration
: "${N8N_API_URL:=http://localhost:5678}"
: "${N8N_API_KEY:=}"

# Check for required tools
_n8n_check() {
    if [ -z "$N8N_API_KEY" ]; then
        echo "Error: N8N_API_KEY not set" >&2
        return 1
    fi
    if ! command -v curl &> /dev/null; then
        echo "Error: curl not found" >&2
        return 1
    fi
    if ! command -v jq &> /dev/null; then
        echo "Error: jq not found (install with: apt install jq)" >&2
        return 1
    fi
    return 0
}

# List all workflows (compact format)
n8n-list() {
    _n8n_check || return 1
    curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
         "$N8N_API_URL/api/v1/workflows" | \
         jq -r '.data[] | "\(.id)\t\(if .active then "✓" else "✗" end)\t\(.name)"' | \
         column -t -s $'\t'
}

# List only active workflows
n8n-active() {
    _n8n_check || return 1
    curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
         "$N8N_API_URL/api/v1/workflows?active=true" | \
         jq -r '.data[] | "\(.id)\t\(.name)"' | \
         column -t -s $'\t'
}

# Get workflow by ID
n8n-get() {
    _n8n_check || return 1
    local id=${1:-}
    if [ -z "$id" ]; then
        echo "Usage: n8n-get <workflow-id>" >&2
        return 1
    fi
    curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
         "$N8N_API_URL/api/v1/workflows/$id" | jq
}

# List recent executions
n8n-exec() {
    _n8n_check || return 1
    local limit=${1:-10}
    curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
         "$N8N_API_URL/api/v1/executions?limit=$limit" | \
         jq -r '.data[] | "\(.id)\t\(.status)\t\(.workflowId)\t\(.startedAt[:19])"' | \
         column -t -s $'\t'
}

# Show recent failed executions
n8n-errors() {
    _n8n_check || return 1
    local limit=${1:-5}
    echo "Recent failed executions:"
    curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
         "$N8N_API_URL/api/v1/executions?status=error&limit=$limit" | \
         jq -r '.data[] | "[\(.id)] workflow:\(.workflowId) \(.startedAt[:19])"'
}

# Trigger a webhook
n8n-trigger() {
    local path=${1:-}
    local data=${2:-"{}"}

    if [ -z "$path" ]; then
        echo "Usage: n8n-trigger <webhook-path> [json-data]" >&2
        return 1
    fi

    curl -s -X POST \
         -H "Content-Type: application/json" \
         -d "$data" \
         "$N8N_API_URL/webhook/$path" | jq
}

# Trigger a test webhook
n8n-trigger-test() {
    local path=${1:-}
    local data=${2:-"{}"}

    if [ -z "$path" ]; then
        echo "Usage: n8n-trigger-test <webhook-path> [json-data]" >&2
        return 1
    fi

    curl -s -X POST \
         -H "Content-Type: application/json" \
         -d "$data" \
         "$N8N_API_URL/webhook-test/$path" | jq
}

# Activate a workflow
n8n-activate() {
    _n8n_check || return 1
    local id=${1:-}
    if [ -z "$id" ]; then
        echo "Usage: n8n-activate <workflow-id>" >&2
        return 1
    fi
    curl -s -X POST -H "X-N8N-API-KEY: $N8N_API_KEY" \
         "$N8N_API_URL/api/v1/workflows/$id/activate" | \
         jq '{id, name, active}'
    echo "Workflow $id activated"
}

# Deactivate a workflow
n8n-deactivate() {
    _n8n_check || return 1
    local id=${1:-}
    if [ -z "$id" ]; then
        echo "Usage: n8n-deactivate <workflow-id>" >&2
        return 1
    fi
    curl -s -X POST -H "X-N8N-API-KEY: $N8N_API_KEY" \
         "$N8N_API_URL/api/v1/workflows/$id/deactivate" | \
         jq '{id, name, active}'
    echo "Workflow $id deactivated"
}

# Export workflow to file
n8n-export() {
    _n8n_check || return 1
    local id=${1:-}
    local output=${2:-"workflow-$id.json"}
    if [ -z "$id" ]; then
        echo "Usage: n8n-export <workflow-id> [output-file]" >&2
        return 1
    fi
    curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
         "$N8N_API_URL/api/v1/workflows/$id" | jq > "$output"
    echo "Exported to $output"
}

# Check n8n health
n8n-health() {
    local status
    status=$(curl -s -o /dev/null -w "%{http_code}" "$N8N_API_URL/healthz" 2>/dev/null || echo "000")

    if [ "$status" = "200" ]; then
        echo "✓ n8n is healthy at $N8N_API_URL"
    else
        echo "✗ n8n is not responding at $N8N_API_URL (HTTP $status)"
        return 1
    fi
}

# Get execution details
n8n-execution() {
    _n8n_check || return 1
    local id=${1:-}
    if [ -z "$id" ]; then
        echo "Usage: n8n-execution <execution-id>" >&2
        return 1
    fi
    curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
         "$N8N_API_URL/api/v1/executions/$id?includeData=true" | jq
}

# Quick debug - get last error details
n8n-last-error() {
    _n8n_check || return 1
    local exec_id
    exec_id=$(curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
              "$N8N_API_URL/api/v1/executions?status=error&limit=1" | \
              jq -r '.data[0].id // empty')

    if [ -z "$exec_id" ]; then
        echo "No failed executions found"
        return 0
    fi

    echo "Last failed execution: $exec_id"
    curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
         "$N8N_API_URL/api/v1/executions/$exec_id" | \
         jq '{
           workflow: .workflowId,
           status: .status,
           startedAt: .startedAt,
           lastNode: .data.resultData.lastNodeExecuted,
           error: .data.resultData.error.message
         }'
}

# Show help
n8n-help() {
    cat << 'EOF'
n8n Quick Actions
=================

Workflow Commands:
  n8n-list              List all workflows
  n8n-active            List active workflows only
  n8n-get <id>          Get workflow details
  n8n-activate <id>     Activate workflow
  n8n-deactivate <id>   Deactivate workflow
  n8n-export <id> [file] Export workflow to JSON

Execution Commands:
  n8n-exec [limit]      List recent executions
  n8n-errors [limit]    Show recent failed executions
  n8n-execution <id>    Get execution details
  n8n-last-error        Debug last failed execution

Webhook Commands:
  n8n-trigger <path> [json]      Trigger production webhook
  n8n-trigger-test <path> [json] Trigger test webhook

Utility Commands:
  n8n-health            Check n8n health
  n8n-help              Show this help

Environment Variables:
  N8N_API_URL           n8n instance URL (default: http://localhost:5678)
  N8N_API_KEY           API key (required)
EOF
}

# Show available commands on source
echo "n8n quick actions loaded. Type 'n8n-help' for commands."
