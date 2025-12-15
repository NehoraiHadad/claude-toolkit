#!/usr/bin/env python3
"""
n8n Workflow CRUD Operations
Python script for managing n8n workflows via REST API.

Usage:
    python workflow-crud.py <command> [arguments]

Environment Variables:
    N8N_API_URL - n8n instance URL (default: http://localhost:5678)
    N8N_API_KEY - API key for authentication
"""

import os
import sys
import json
import argparse
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime

# Configuration
N8N_URL = os.getenv('N8N_API_URL', 'http://localhost:5678')
API_KEY = os.getenv('N8N_API_KEY', '')


class N8nClient:
    """n8n REST API client."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'X-N8N-API-KEY': api_key,
            'Content-Type': 'application/json'
        })

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make API request."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, json=data, timeout=30)
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}", file=sys.stderr)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    print(f"Response: {e.response.json()}", file=sys.stderr)
                except Exception:
                    print(f"Response: {e.response.text}", file=sys.stderr)
            sys.exit(1)

    # Workflow operations

    def list_workflows(self, active_only: bool = False, limit: int = 100) -> List[Dict]:
        """List all workflows."""
        params = f"?limit={limit}"
        if active_only:
            params += "&active=true"
        result = self._request('GET', f'/api/v1/workflows{params}')
        return result.get('data', [])

    def get_workflow(self, workflow_id: str) -> Dict:
        """Get workflow by ID."""
        return self._request('GET', f'/api/v1/workflows/{workflow_id}')

    def create_workflow(self, workflow_data: Dict) -> Dict:
        """Create a new workflow."""
        return self._request('POST', '/api/v1/workflows', workflow_data)

    def update_workflow(self, workflow_id: str, workflow_data: Dict) -> Dict:
        """Update existing workflow."""
        return self._request('PUT', f'/api/v1/workflows/{workflow_id}', workflow_data)

    def delete_workflow(self, workflow_id: str) -> None:
        """Delete workflow."""
        self._request('DELETE', f'/api/v1/workflows/{workflow_id}')

    def activate_workflow(self, workflow_id: str) -> Dict:
        """Activate workflow."""
        return self._request('POST', f'/api/v1/workflows/{workflow_id}/activate')

    def deactivate_workflow(self, workflow_id: str) -> Dict:
        """Deactivate workflow."""
        return self._request('POST', f'/api/v1/workflows/{workflow_id}/deactivate')

    # Execution operations

    def list_executions(
        self,
        workflow_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """List executions with optional filters."""
        params = [f"limit={limit}"]
        if workflow_id:
            params.append(f"workflowId={workflow_id}")
        if status:
            params.append(f"status={status}")
        query = '&'.join(params)
        result = self._request('GET', f'/api/v1/executions?{query}')
        return result.get('data', [])

    def get_execution(self, execution_id: str, include_data: bool = True) -> Dict:
        """Get execution details."""
        return self._request(
            'GET',
            f'/api/v1/executions/{execution_id}?includeData={str(include_data).lower()}'
        )

    def delete_execution(self, execution_id: str) -> None:
        """Delete execution."""
        self._request('DELETE', f'/api/v1/executions/{execution_id}')

    # Webhook operations

    def trigger_webhook(self, path: str, data: Dict = None, test: bool = False) -> Dict:
        """Trigger webhook."""
        endpoint = 'webhook-test' if test else 'webhook'
        url = f"{self.base_url}/{endpoint}/{path}"
        response = requests.post(url, json=data or {}, timeout=30)
        try:
            return response.json()
        except Exception:
            return {'response': response.text, 'status_code': response.status_code}


def format_workflow(workflow: Dict, verbose: bool = False) -> str:
    """Format workflow for display."""
    if verbose:
        return json.dumps(workflow, indent=2)

    active = "✓" if workflow.get('active') else "✗"
    nodes = len(workflow.get('nodes', []))
    return f"[{workflow['id']}] {active} {workflow['name']} ({nodes} nodes)"


def format_execution(execution: Dict) -> str:
    """Format execution for display."""
    status_icons = {'success': '✓', 'error': '✗', 'waiting': '⏳', 'running': '▶'}
    status = execution.get('status', 'unknown')
    icon = status_icons.get(status, '?')
    started = execution.get('startedAt', 'N/A')
    if started != 'N/A':
        started = started[:19].replace('T', ' ')
    return f"[{execution['id']}] {icon} {status:8} workflow:{execution.get('workflowId', 'N/A')} {started}"


# Commands

def cmd_list(client: N8nClient, args):
    """List workflows."""
    workflows = client.list_workflows(active_only=args.active)
    if args.json:
        print(json.dumps(workflows, indent=2))
    else:
        for wf in workflows:
            print(format_workflow(wf))
        print(f"\nTotal: {len(workflows)} workflows")


def cmd_get(client: N8nClient, args):
    """Get workflow."""
    workflow = client.get_workflow(args.id)
    if args.json or args.verbose:
        print(json.dumps(workflow, indent=2))
    else:
        print(format_workflow(workflow))
        print(f"\nNodes ({len(workflow.get('nodes', []))}):")
        for node in workflow.get('nodes', []):
            print(f"  - {node['name']} ({node['type']})")


def cmd_create(client: N8nClient, args):
    """Create workflow from file."""
    with open(args.file, 'r') as f:
        workflow_data = json.load(f)

    result = client.create_workflow(workflow_data)
    print(f"Created workflow: {format_workflow(result)}")


def cmd_update(client: N8nClient, args):
    """Update workflow from file."""
    with open(args.file, 'r') as f:
        workflow_data = json.load(f)

    result = client.update_workflow(args.id, workflow_data)
    print(f"Updated workflow: {format_workflow(result)}")


def cmd_delete(client: N8nClient, args):
    """Delete workflow."""
    if not args.force:
        confirm = input(f"Delete workflow {args.id}? [y/N] ")
        if confirm.lower() != 'y':
            print("Cancelled")
            return

    client.delete_workflow(args.id)
    print(f"Deleted workflow {args.id}")


def cmd_activate(client: N8nClient, args):
    """Activate workflow."""
    result = client.activate_workflow(args.id)
    print(f"Activated: {format_workflow(result)}")


def cmd_deactivate(client: N8nClient, args):
    """Deactivate workflow."""
    result = client.deactivate_workflow(args.id)
    print(f"Deactivated: {format_workflow(result)}")


def cmd_export(client: N8nClient, args):
    """Export workflow to file."""
    workflow = client.get_workflow(args.id)
    output = args.output or f"workflow-{args.id}.json"

    with open(output, 'w') as f:
        json.dump(workflow, f, indent=2)

    print(f"Exported to {output}")


def cmd_executions(client: N8nClient, args):
    """List executions."""
    executions = client.list_executions(
        workflow_id=args.workflow,
        status=args.status,
        limit=args.limit
    )

    if args.json:
        print(json.dumps(executions, indent=2))
    else:
        for ex in executions:
            print(format_execution(ex))
        print(f"\nTotal: {len(executions)} executions")


def cmd_execution(client: N8nClient, args):
    """Get execution details."""
    execution = client.get_execution(args.id)

    if args.json:
        print(json.dumps(execution, indent=2))
    else:
        print(format_execution(execution))
        print(f"\nMode: {execution.get('mode', 'N/A')}")

        # Show node execution times
        run_data = execution.get('data', {}).get('resultData', {}).get('runData', {})
        if run_data:
            print("\nNode execution times:")
            for node_name, node_data in run_data.items():
                if node_data:
                    exec_time = node_data[0].get('executionTime', 'N/A')
                    print(f"  - {node_name}: {exec_time}ms")

        # Show error if any
        error = execution.get('data', {}).get('resultData', {}).get('error')
        if error:
            print(f"\nError: {error.get('message', error)}")


def cmd_trigger(client: N8nClient, args):
    """Trigger webhook."""
    data = {}
    if args.data:
        data = json.loads(args.data)
    elif args.file:
        with open(args.file, 'r') as f:
            data = json.load(f)

    result = client.trigger_webhook(args.path, data, test=args.test)
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description='n8n Workflow CRUD Operations')
    parser.add_argument('--url', default=N8N_URL, help='n8n API URL')
    parser.add_argument('--key', default=API_KEY, help='API key')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # List workflows
    p_list = subparsers.add_parser('list', help='List workflows')
    p_list.add_argument('--active', action='store_true', help='Only active workflows')
    p_list.add_argument('--json', action='store_true', help='JSON output')

    # Get workflow
    p_get = subparsers.add_parser('get', help='Get workflow')
    p_get.add_argument('id', help='Workflow ID')
    p_get.add_argument('--json', action='store_true', help='JSON output')
    p_get.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    # Create workflow
    p_create = subparsers.add_parser('create', help='Create workflow')
    p_create.add_argument('file', help='JSON file path')

    # Update workflow
    p_update = subparsers.add_parser('update', help='Update workflow')
    p_update.add_argument('id', help='Workflow ID')
    p_update.add_argument('file', help='JSON file path')

    # Delete workflow
    p_delete = subparsers.add_parser('delete', help='Delete workflow')
    p_delete.add_argument('id', help='Workflow ID')
    p_delete.add_argument('--force', '-f', action='store_true', help='Skip confirmation')

    # Activate workflow
    p_activate = subparsers.add_parser('activate', help='Activate workflow')
    p_activate.add_argument('id', help='Workflow ID')

    # Deactivate workflow
    p_deactivate = subparsers.add_parser('deactivate', help='Deactivate workflow')
    p_deactivate.add_argument('id', help='Workflow ID')

    # Export workflow
    p_export = subparsers.add_parser('export', help='Export workflow to file')
    p_export.add_argument('id', help='Workflow ID')
    p_export.add_argument('output', nargs='?', help='Output file path')

    # List executions
    p_execs = subparsers.add_parser('executions', help='List executions')
    p_execs.add_argument('--workflow', '-w', help='Filter by workflow ID')
    p_execs.add_argument('--status', '-s', choices=['success', 'error', 'waiting'],
                         help='Filter by status')
    p_execs.add_argument('--limit', '-l', type=int, default=20, help='Limit results')
    p_execs.add_argument('--json', action='store_true', help='JSON output')

    # Get execution
    p_exec = subparsers.add_parser('execution', help='Get execution details')
    p_exec.add_argument('id', help='Execution ID')
    p_exec.add_argument('--json', action='store_true', help='JSON output')

    # Trigger webhook
    p_trigger = subparsers.add_parser('trigger', help='Trigger webhook')
    p_trigger.add_argument('path', help='Webhook path')
    p_trigger.add_argument('--data', '-d', help='JSON data string')
    p_trigger.add_argument('--file', '-f', help='JSON data file')
    p_trigger.add_argument('--test', '-t', action='store_true', help='Use test webhook')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if not args.key:
        print("Error: N8N_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = N8nClient(args.url, args.key)

    commands = {
        'list': cmd_list,
        'get': cmd_get,
        'create': cmd_create,
        'update': cmd_update,
        'delete': cmd_delete,
        'activate': cmd_activate,
        'deactivate': cmd_deactivate,
        'export': cmd_export,
        'executions': cmd_executions,
        'execution': cmd_execution,
        'trigger': cmd_trigger,
    }

    commands[args.command](client, args)


if __name__ == '__main__':
    main()
