#!/bin/bash
# n8n API Wrapper Script
# Usage: n8n-api.sh <command> [arguments]
#
# Environment Variables:
#   N8N_API_URL - n8n instance URL (default: http://localhost:5678)
#   N8N_API_KEY - API key for authentication

set -euo pipefail

# Configuration
N8N_URL="${N8N_API_URL:-http://localhost:5678}"
API_KEY="${N8N_API_KEY:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Validate API key
check_auth() {
    if [ -z "$API_KEY" ]; then
        echo -e "${RED}Error: N8N_API_KEY environment variable not set${NC}" >&2
        exit 1
    fi
}

# Make API request
api_request() {
    local method=$1
    local endpoint=$2
    local data=${3:-}

    local args=(-s -X "$method" -H "X-N8N-API-KEY: $API_KEY" -H "Content-Type: application/json")

    if [ -n "$data" ]; then
        args+=(-d "$data")
    fi

    curl "${args[@]}" "$N8N_URL$endpoint"
}

# Commands

cmd_list_workflows() {
    check_auth
    local active_filter=""
    if [ "${1:-}" = "--active" ]; then
        active_filter="?active=true"
    fi
    api_request GET "/api/v1/workflows$active_filter" | jq '.data[] | {id, name, active}'
}

cmd_get_workflow() {
    check_auth
    local id=${1:-}
    if [ -z "$id" ]; then
        echo -e "${RED}Error: Workflow ID required${NC}" >&2
        echo "Usage: $0 get-workflow <id>" >&2
        exit 1
    fi
    api_request GET "/api/v1/workflows/$id" | jq
}

cmd_create_workflow() {
    check_auth
    local file=${1:-}
    if [ -z "$file" ] || [ ! -f "$file" ]; then
        echo -e "${RED}Error: Valid JSON file required${NC}" >&2
        echo "Usage: $0 create-workflow <file.json>" >&2
        exit 1
    fi
    api_request POST "/api/v1/workflows" "$(cat "$file")" | jq '{id, name, active}'
}

cmd_update_workflow() {
    check_auth
    local id=${1:-}
    local file=${2:-}
    if [ -z "$id" ] || [ -z "$file" ] || [ ! -f "$file" ]; then
        echo -e "${RED}Error: Workflow ID and valid JSON file required${NC}" >&2
        echo "Usage: $0 update-workflow <id> <file.json>" >&2
        exit 1
    fi
    api_request PUT "/api/v1/workflows/$id" "$(cat "$file")" | jq '{id, name, active}'
}

cmd_delete_workflow() {
    check_auth
    local id=${1:-}
    if [ -z "$id" ]; then
        echo -e "${RED}Error: Workflow ID required${NC}" >&2
        echo "Usage: $0 delete-workflow <id>" >&2
        exit 1
    fi
    api_request DELETE "/api/v1/workflows/$id"
    echo -e "${GREEN}Workflow $id deleted${NC}"
}

cmd_activate() {
    check_auth
    local id=${1:-}
    if [ -z "$id" ]; then
        echo -e "${RED}Error: Workflow ID required${NC}" >&2
        exit 1
    fi
    api_request POST "/api/v1/workflows/$id/activate" | jq '{id, name, active}'
    echo -e "${GREEN}Workflow $id activated${NC}"
}

cmd_deactivate() {
    check_auth
    local id=${1:-}
    if [ -z "$id" ]; then
        echo -e "${RED}Error: Workflow ID required${NC}" >&2
        exit 1
    fi
    api_request POST "/api/v1/workflows/$id/deactivate" | jq '{id, name, active}'
    echo -e "${YELLOW}Workflow $id deactivated${NC}"
}

cmd_list_executions() {
    check_auth
    local workflow_id=${1:-}
    local status=${2:-}
    local params="?limit=20"

    if [ -n "$workflow_id" ]; then
        params="${params}&workflowId=$workflow_id"
    fi
    if [ -n "$status" ]; then
        params="${params}&status=$status"
    fi

    api_request GET "/api/v1/executions$params" | \
        jq '.data[] | {id, workflowId, status, startedAt, mode}'
}

cmd_get_execution() {
    check_auth
    local id=${1:-}
    if [ -z "$id" ]; then
        echo -e "${RED}Error: Execution ID required${NC}" >&2
        exit 1
    fi
    api_request GET "/api/v1/executions/$id?includeData=true" | jq
}

cmd_trigger() {
    local path=${1:-}
    local data=${2:-"{}"}

    if [ -z "$path" ]; then
        echo -e "${RED}Error: Webhook path required${NC}" >&2
        echo "Usage: $0 trigger <webhook-path> [json-data]" >&2
        exit 1
    fi

    curl -s -X POST \
         -H "Content-Type: application/json" \
         -d "$data" \
         "$N8N_URL/webhook/$path"
}

cmd_trigger_test() {
    local path=${1:-}
    local data=${2:-"{}"}

    if [ -z "$path" ]; then
        echo -e "${RED}Error: Webhook path required${NC}" >&2
        exit 1
    fi

    curl -s -X POST \
         -H "Content-Type: application/json" \
         -d "$data" \
         "$N8N_URL/webhook-test/$path"
}

cmd_errors() {
    check_auth
    local limit=${1:-10}
    api_request GET "/api/v1/executions?status=error&limit=$limit" | \
        jq '.data[] | {id, workflowId, startedAt, lastNode: .data.resultData.lastNodeExecuted}'
}

cmd_export() {
    check_auth
    local id=${1:-}
    local output=${2:-"workflow-$id.json"}
    if [ -z "$id" ]; then
        echo -e "${RED}Error: Workflow ID required${NC}" >&2
        exit 1
    fi
    api_request GET "/api/v1/workflows/$id" | jq > "$output"
    echo -e "${GREEN}Exported to $output${NC}"
}

cmd_health() {
    local result
    result=$(curl -s -o /dev/null -w "%{http_code}" "$N8N_URL/healthz" 2>/dev/null || echo "000")

    if [ "$result" = "200" ]; then
        echo -e "${GREEN}n8n is healthy ($N8N_URL)${NC}"
    else
        echo -e "${RED}n8n is not responding ($N8N_URL) - HTTP $result${NC}"
        exit 1
    fi
}

cmd_help() {
    cat << EOF
n8n API Wrapper Script

Usage: $0 <command> [arguments]

Workflow Commands:
  list-workflows [--active]     List all workflows (optionally only active)
  get-workflow <id>            Get workflow by ID
  create-workflow <file>       Create workflow from JSON file
  update-workflow <id> <file>  Update workflow from JSON file
  delete-workflow <id>         Delete workflow
  activate <id>                Activate workflow
  deactivate <id>              Deactivate workflow
  export <id> [output]         Export workflow to JSON file

Execution Commands:
  list-executions [workflow-id] [status]  List executions
  get-execution <id>           Get execution details
  errors [limit]               List recent failed executions

Webhook Commands:
  trigger <path> [json]        Trigger webhook (production)
  trigger-test <path> [json]   Trigger webhook (test mode)

Utility Commands:
  health                       Check n8n health
  help                         Show this help

Environment Variables:
  N8N_API_URL                  n8n instance URL (default: http://localhost:5678)
  N8N_API_KEY                  API key for authentication (required)

Examples:
  $0 list-workflows
  $0 get-workflow 1
  $0 create-workflow my-workflow.json
  $0 activate 1
  $0 trigger my-webhook '{"data": "test"}'
  $0 errors 5
EOF
}

# Main
case "${1:-help}" in
    list-workflows)   shift; cmd_list_workflows "$@" ;;
    get-workflow)     shift; cmd_get_workflow "$@" ;;
    create-workflow)  shift; cmd_create_workflow "$@" ;;
    update-workflow)  shift; cmd_update_workflow "$@" ;;
    delete-workflow)  shift; cmd_delete_workflow "$@" ;;
    activate)         shift; cmd_activate "$@" ;;
    deactivate)       shift; cmd_deactivate "$@" ;;
    list-executions)  shift; cmd_list_executions "$@" ;;
    get-execution)    shift; cmd_get_execution "$@" ;;
    trigger)          shift; cmd_trigger "$@" ;;
    trigger-test)     shift; cmd_trigger_test "$@" ;;
    errors)           shift; cmd_errors "$@" ;;
    export)           shift; cmd_export "$@" ;;
    health)           cmd_health ;;
    help|--help|-h)   cmd_help ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}" >&2
        echo "Run '$0 help' for usage" >&2
        exit 1
        ;;
esac
