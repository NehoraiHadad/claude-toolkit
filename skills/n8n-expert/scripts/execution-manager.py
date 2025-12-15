#!/usr/bin/env python3
"""
n8n Execution Manager
Debug and monitor n8n workflow executions.

Usage:
    python execution-manager.py <command> [arguments]

Environment Variables:
    N8N_API_URL - n8n instance URL (default: http://localhost:5678)
    N8N_API_KEY - API key for authentication
"""

import os
import sys
import json
import argparse
import requests
from typing import Optional, Dict, List
from datetime import datetime, timedelta

# Configuration
N8N_URL = os.getenv('N8N_API_URL', 'http://localhost:5678')
API_KEY = os.getenv('N8N_API_KEY', '')


class ExecutionManager:
    """Manage and debug n8n executions."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'X-N8N-API-KEY': api_key,
            'Content-Type': 'application/json'
        }

    def _get(self, endpoint: str) -> Dict:
        """Make GET request."""
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()

    def list_executions(
        self,
        workflow_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """List executions with filters."""
        params = [f"limit={limit}"]
        if workflow_id:
            params.append(f"workflowId={workflow_id}")
        if status:
            params.append(f"status={status}")
        query = '&'.join(params)
        result = self._get(f'/api/v1/executions?{query}')
        return result.get('data', [])

    def get_execution(self, execution_id: str) -> Dict:
        """Get execution with full data."""
        return self._get(f'/api/v1/executions/{execution_id}?includeData=true')

    def get_workflow(self, workflow_id: str) -> Dict:
        """Get workflow info."""
        return self._get(f'/api/v1/workflows/{workflow_id}')


def format_timestamp(ts: str) -> str:
    """Format ISO timestamp."""
    if not ts:
        return 'N/A'
    return ts[:19].replace('T', ' ')


def format_duration(start: str, stop: str) -> str:
    """Calculate duration between timestamps."""
    if not start or not stop:
        return 'N/A'
    try:
        start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
        stop_dt = datetime.fromisoformat(stop.replace('Z', '+00:00'))
        duration = stop_dt - start_dt
        total_seconds = duration.total_seconds()
        if total_seconds < 1:
            return f"{int(total_seconds * 1000)}ms"
        elif total_seconds < 60:
            return f"{total_seconds:.1f}s"
        else:
            minutes = int(total_seconds // 60)
            seconds = int(total_seconds % 60)
            return f"{minutes}m {seconds}s"
    except Exception:
        return 'N/A'


def cmd_list(manager: ExecutionManager, args):
    """List executions."""
    executions = manager.list_executions(
        workflow_id=args.workflow_id,
        status=args.status,
        limit=args.limit
    )

    status_icons = {
        'success': '✓',
        'error': '✗',
        'waiting': '⏳',
        'running': '▶',
        'unknown': '?'
    }

    print(f"{'ID':<10} {'Status':<10} {'Workflow':<10} {'Started':<20} {'Duration':<10}")
    print("-" * 70)

    for ex in executions:
        status = ex.get('status', 'unknown')
        icon = status_icons.get(status, '?')
        duration = format_duration(ex.get('startedAt'), ex.get('stoppedAt'))

        print(f"{ex['id']:<10} {icon} {status:<8} {ex.get('workflowId', 'N/A'):<10} "
              f"{format_timestamp(ex.get('startedAt')):<20} {duration:<10}")

    print(f"\nTotal: {len(executions)} executions")


def cmd_get(manager: ExecutionManager, args):
    """Get execution details."""
    execution = manager.get_execution(args.id)

    print(f"Execution: {execution['id']}")
    print(f"Workflow:  {execution.get('workflowId', 'N/A')}")
    print(f"Status:    {execution.get('status', 'N/A')}")
    print(f"Mode:      {execution.get('mode', 'N/A')}")
    print(f"Started:   {format_timestamp(execution.get('startedAt'))}")
    print(f"Stopped:   {format_timestamp(execution.get('stoppedAt'))}")
    print(f"Duration:  {format_duration(execution.get('startedAt'), execution.get('stoppedAt'))}")

    # Error info
    error = execution.get('data', {}).get('resultData', {}).get('error')
    if error:
        print(f"\n--- ERROR ---")
        print(f"Message: {error.get('message', str(error))}")
        if error.get('stack'):
            print(f"Stack: {error['stack'][:500]}...")

    if args.json:
        print(f"\n--- Full JSON ---")
        print(json.dumps(execution, indent=2))


def cmd_debug(manager: ExecutionManager, args):
    """Detailed debug output for execution."""
    execution = manager.get_execution(args.id)

    print("=" * 80)
    print(f"EXECUTION DEBUG: {execution['id']}")
    print("=" * 80)

    # Basic info
    print(f"\nWorkflow ID: {execution.get('workflowId')}")
    print(f"Status:      {execution.get('status')}")
    print(f"Mode:        {execution.get('mode')}")
    print(f"Started:     {format_timestamp(execution.get('startedAt'))}")
    print(f"Stopped:     {format_timestamp(execution.get('stoppedAt'))}")
    print(f"Duration:    {format_duration(execution.get('startedAt'), execution.get('stoppedAt'))}")

    # Get workflow name
    try:
        workflow = manager.get_workflow(execution.get('workflowId'))
        print(f"Workflow:    {workflow.get('name')}")
    except Exception:
        pass

    # Node execution details
    run_data = execution.get('data', {}).get('resultData', {}).get('runData', {})

    if run_data:
        print("\n" + "-" * 40)
        print("NODE EXECUTION DETAILS")
        print("-" * 40)

        # Sort by execution time
        node_times = []
        for node_name, node_data in run_data.items():
            if node_data:
                exec_time = node_data[0].get('executionTime', 0)
                node_times.append((node_name, exec_time, node_data[0]))

        node_times.sort(key=lambda x: x[0])  # Sort by name for execution order

        for node_name, exec_time, data in node_times:
            status = "✓" if 'error' not in data else "✗"
            items_out = 0
            if data.get('data', {}).get('main'):
                for branch in data['data']['main']:
                    if branch:
                        items_out += len(branch)

            print(f"\n{status} {node_name}")
            print(f"   Execution time: {exec_time}ms")
            print(f"   Items output: {items_out}")

            # Show error if any
            if 'error' in data:
                print(f"   ERROR: {data['error'].get('message', data['error'])}")

            # Show sample data (first item)
            if args.verbose and data.get('data', {}).get('main'):
                for i, branch in enumerate(data['data']['main']):
                    if branch and len(branch) > 0:
                        print(f"   Output[{i}] sample: {json.dumps(branch[0].get('json', {}), indent=6)[:200]}...")

    # Last node executed
    last_node = execution.get('data', {}).get('resultData', {}).get('lastNodeExecuted')
    if last_node:
        print(f"\nLast node executed: {last_node}")

    # Error details
    error = execution.get('data', {}).get('resultData', {}).get('error')
    if error:
        print("\n" + "=" * 40)
        print("ERROR DETAILS")
        print("=" * 40)
        print(f"Message: {error.get('message', str(error))}")
        print(f"Node: {error.get('node', 'N/A')}")
        if error.get('description'):
            print(f"Description: {error['description']}")
        if error.get('stack') and args.verbose:
            print(f"\nStack trace:\n{error['stack']}")


def cmd_errors(manager: ExecutionManager, args):
    """List recent failed executions."""
    executions = manager.list_executions(status='error', limit=args.limit)

    if not executions:
        print("No failed executions found")
        return

    print(f"Recent Failed Executions (last {args.limit}):")
    print("-" * 80)

    for ex in executions:
        execution = manager.get_execution(ex['id'])
        error = execution.get('data', {}).get('resultData', {}).get('error', {})
        last_node = execution.get('data', {}).get('resultData', {}).get('lastNodeExecuted', 'N/A')

        print(f"\n[{ex['id']}] Workflow: {ex.get('workflowId')} | {format_timestamp(ex.get('startedAt'))}")
        print(f"  Last node: {last_node}")
        print(f"  Error: {error.get('message', 'Unknown error')[:100]}")


def cmd_stats(manager: ExecutionManager, args):
    """Show execution statistics."""
    all_execs = manager.list_executions(
        workflow_id=args.workflow_id,
        limit=100
    )

    if not all_execs:
        print("No executions found")
        return

    # Count by status
    status_counts = {}
    total_duration = 0
    count_with_duration = 0

    for ex in all_execs:
        status = ex.get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1

        if ex.get('startedAt') and ex.get('stoppedAt'):
            try:
                start = datetime.fromisoformat(ex['startedAt'].replace('Z', '+00:00'))
                stop = datetime.fromisoformat(ex['stoppedAt'].replace('Z', '+00:00'))
                total_duration += (stop - start).total_seconds()
                count_with_duration += 1
            except Exception:
                pass

    print("Execution Statistics")
    print("-" * 40)
    print(f"Total executions: {len(all_execs)}")

    for status, count in sorted(status_counts.items()):
        pct = count / len(all_execs) * 100
        print(f"  {status}: {count} ({pct:.1f}%)")

    if count_with_duration > 0:
        avg_duration = total_duration / count_with_duration
        print(f"\nAverage duration: {avg_duration:.2f}s")

    # Success rate
    success = status_counts.get('success', 0)
    error = status_counts.get('error', 0)
    if success + error > 0:
        success_rate = success / (success + error) * 100
        print(f"Success rate: {success_rate:.1f}%")


def cmd_watch(manager: ExecutionManager, args):
    """Watch for new executions."""
    import time

    print(f"Watching for executions... (Ctrl+C to stop)")
    print("-" * 60)

    seen_ids = set()
    last_check = None

    while True:
        try:
            executions = manager.list_executions(
                workflow_id=args.workflow_id,
                limit=10
            )

            for ex in reversed(executions):
                if ex['id'] not in seen_ids:
                    seen_ids.add(ex['id'])
                    if last_check is not None:  # Skip first batch
                        status_icons = {'success': '✓', 'error': '✗', 'waiting': '⏳', 'running': '▶'}
                        icon = status_icons.get(ex.get('status', ''), '?')
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] {icon} "
                              f"Execution {ex['id']} - Workflow {ex.get('workflowId')} - "
                              f"{ex.get('status')}")

            last_check = datetime.now()
            time.sleep(args.interval)

        except KeyboardInterrupt:
            print("\nStopped")
            break


def main():
    parser = argparse.ArgumentParser(description='n8n Execution Manager')
    parser.add_argument('--url', default=N8N_URL, help='n8n API URL')
    parser.add_argument('--key', default=API_KEY, help='API key')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # List executions
    p_list = subparsers.add_parser('list', help='List executions')
    p_list.add_argument('--workflow-id', '-w', help='Filter by workflow')
    p_list.add_argument('--status', '-s', choices=['success', 'error', 'waiting'])
    p_list.add_argument('--limit', '-l', type=int, default=20)

    # Get execution
    p_get = subparsers.add_parser('get', help='Get execution details')
    p_get.add_argument('id', help='Execution ID')
    p_get.add_argument('--json', action='store_true', help='Full JSON output')

    # Debug execution
    p_debug = subparsers.add_parser('debug', help='Debug execution (detailed)')
    p_debug.add_argument('id', help='Execution ID')
    p_debug.add_argument('--verbose', '-v', action='store_true', help='Include data samples')

    # List errors
    p_errors = subparsers.add_parser('errors', help='List recent errors')
    p_errors.add_argument('--limit', '-l', type=int, default=10)

    # Statistics
    p_stats = subparsers.add_parser('stats', help='Execution statistics')
    p_stats.add_argument('--workflow-id', '-w', help='Filter by workflow')

    # Watch
    p_watch = subparsers.add_parser('watch', help='Watch for new executions')
    p_watch.add_argument('--workflow-id', '-w', help='Filter by workflow')
    p_watch.add_argument('--interval', '-i', type=int, default=5, help='Check interval (seconds)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if not args.key:
        print("Error: N8N_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    manager = ExecutionManager(args.url, args.key)

    commands = {
        'list': cmd_list,
        'get': cmd_get,
        'debug': cmd_debug,
        'errors': cmd_errors,
        'stats': cmd_stats,
        'watch': cmd_watch,
    }

    try:
        commands[args.command](manager, args)
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
