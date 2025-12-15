# n8n Debugging and Troubleshooting Guide

Comprehensive guide for debugging n8n workflow issues and troubleshooting common problems.

## Debugging Workflow: Overview

1. **Check Execution Status** - Did the workflow run?
2. **Review Execution Data** - What data flowed through?
3. **Identify Error Node** - Where did it fail?
4. **Analyze Error Message** - What went wrong?
5. **Check Node Configuration** - Is it configured correctly?
6. **Verify Data Format** - Is the data what you expected?

---

## Checking Executions via API

### List Recent Executions
```bash
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
     "$N8N_API_URL/api/v1/executions?limit=20" | \
     jq '.data[] | {id, workflowId, status, startedAt, mode}'
```

### Filter Failed Executions
```bash
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
     "$N8N_API_URL/api/v1/executions?status=error&limit=10" | jq '.data'
```

### Get Execution Details
```bash
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
     "$N8N_API_URL/api/v1/executions/123?includeData=true" | jq
```

### Extract Error Information
```bash
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
     "$N8N_API_URL/api/v1/executions/123" | \
     jq '.data.resultData.error'
```

### Get Node-by-Node Results
```bash
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
     "$N8N_API_URL/api/v1/executions/123" | \
     jq '.data.resultData.runData | to_entries[] | {node: .key, items: (.value[0].data.main[0] | length), executionTime: .value[0].executionTime}'
```

---

## Common Error Patterns

### 1. Connection Timeout
**Symptom:** `ETIMEDOUT` or `Connection timeout`

**Causes:**
- Target service is down
- Network issues
- Firewall blocking
- Slow response

**Solutions:**
```json
// Increase timeout in HTTP Request node
{
  "options": {
    "timeout": 60000
  }
}
```

```bash
# Test connectivity
curl -v https://target-api.com/health
```

### 2. Authentication Failed
**Symptom:** `401 Unauthorized` or `403 Forbidden`

**Causes:**
- Invalid credentials
- Expired token
- Wrong credential type
- Missing permissions

**Solutions:**
- Verify credentials in n8n Settings
- Check API key hasn't expired
- Confirm correct auth method (header, OAuth, etc.)
- Verify user permissions on target system

### 3. Invalid JSON
**Symptom:** `Unexpected token` or `JSON parse error`

**Causes:**
- Malformed JSON input
- Expression returning non-JSON
- Missing quotes or brackets

**Debug:**
```javascript
// In Code node, validate JSON
const input = $json.data;
try {
  const parsed = JSON.parse(input);
  return [{json: {valid: true, data: parsed}}];
} catch(e) {
  return [{json: {valid: false, error: e.message, input: input}}];
}
```

### 4. Expression Evaluation Error
**Symptom:** `Cannot read property of undefined`

**Causes:**
- Missing field in data
- Wrong node reference
- Typo in field name

**Debug:**
```javascript
// Check if field exists
$json.field ?? 'default'

// Safe navigation
$json.nested?.field?.value

// Debug expression output
{{ JSON.stringify($json) }}
```

### 5. Rate Limiting
**Symptom:** `429 Too Many Requests`

**Solutions:**
```json
// Add delay between items
{
  "type": "n8n-nodes-base.wait",
  "parameters": {
    "amount": 1,
    "unit": "seconds"
  }
}
```

```json
// Use Split in Batches
{
  "type": "n8n-nodes-base.splitInBatches",
  "parameters": {
    "batchSize": 10
  }
}
```

### 6. Data Type Mismatch
**Symptom:** `Expected string but got object`

**Debug:**
```javascript
// Check type in Code node
const data = $json.field;
return [{json: {
  value: data,
  type: typeof data,
  isArray: Array.isArray(data)
}}];
```

**Fix:**
```javascript
// Convert types
String($json.number)
Number($json.string)
JSON.stringify($json.object)
JSON.parse($json.string)
```

---

## Debug Strategies

### 1. Add Debug Nodes

Insert Set nodes to capture intermediate state:
```json
{
  "name": "Debug: After Transform",
  "type": "n8n-nodes-base.set",
  "parameters": {
    "mode": "raw",
    "jsonOutput": "={{ { debugTimestamp: $now.toISO(), debugData: $json } }}"
  }
}
```

### 2. Use Code Node for Inspection

```javascript
// Log everything about current state
const debugInfo = {
  currentItem: $json,
  allItems: $input.all().length,
  workflow: $workflow.name,
  execution: $execution.id,
  prevNode: $prevNode.name,
  env: Object.keys($env)
};

console.log(JSON.stringify(debugInfo, null, 2));
return [{json: debugInfo}];
```

### 3. Test with Minimal Data

Create a test webhook with simplified data:
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"test": true, "simple": "data"}' \
     "$N8N_API_URL/webhook-test/my-webhook"
```

### 4. Check Execution via API

```python
import requests

def debug_execution(execution_id):
    headers = {'X-N8N-API-KEY': API_KEY}
    url = f'{N8N_URL}/api/v1/executions/{execution_id}'

    response = requests.get(url, headers=headers)
    execution = response.json()

    print(f"Status: {execution['status']}")
    print(f"Mode: {execution['mode']}")

    if execution.get('data', {}).get('resultData', {}).get('error'):
        print(f"Error: {execution['data']['resultData']['error']}")

    # Print node-by-node results
    run_data = execution.get('data', {}).get('resultData', {}).get('runData', {})
    for node_name, node_data in run_data.items():
        print(f"\n{node_name}:")
        print(f"  Execution time: {node_data[0].get('executionTime')}ms")
        if 'error' in node_data[0]:
            print(f"  Error: {node_data[0]['error']}")
```

---

## Workflow-Level Debugging

### Enable Detailed Logging

In workflow settings:
```json
{
  "settings": {
    "saveDataSuccessExecution": "all",
    "saveDataErrorExecution": "all",
    "saveExecutionProgress": true
  }
}
```

### Error Workflow

Set up a dedicated error handler workflow:
```json
{
  "settings": {
    "errorWorkflow": "error-handler-workflow-id"
  }
}
```

Error workflow receives:
```json
{
  "execution": {
    "id": "123",
    "url": "http://localhost:5678/execution/123",
    "error": {
      "message": "Error message",
      "stack": "Error stack trace"
    },
    "lastNodeExecuted": "Problem Node",
    "mode": "webhook"
  },
  "workflow": {
    "id": "1",
    "name": "My Workflow"
  }
}
```

---

## Node-Specific Debugging

### HTTP Request Node

**Debug request details:**
```json
{
  "options": {
    "response": {
      "response": {
        "fullResponse": true
      }
    }
  }
}
```

Returns:
```json
{
  "statusCode": 200,
  "headers": {...},
  "body": {...}
}
```

### Code Node

**Add logging:**
```javascript
console.log('Input:', JSON.stringify($json));

// Your code here

console.log('Output:', JSON.stringify(result));
return result;
```

View logs in n8n execution details.

### Webhook Node

**Check incoming data:**
```json
{
  "options": {
    "rawBody": true
  }
}
```

Then examine `$json.body` and `$json.headers`.

---

## Performance Debugging

### Identify Slow Nodes

```bash
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
     "$N8N_API_URL/api/v1/executions/123" | \
     jq '.data.resultData.runData | to_entries | sort_by(.value[0].executionTime) | reverse | .[:5] | .[] | {node: .key, ms: .value[0].executionTime}'
```

### Check Execution Duration

```bash
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
     "$N8N_API_URL/api/v1/executions/123" | \
     jq '{
       started: .startedAt,
       stopped: .stoppedAt,
       duration_ms: ((.stoppedAt | fromdateiso8601) - (.startedAt | fromdateiso8601)) * 1000
     }'
```

### Memory Issues

If workflows fail with memory errors:
1. Process data in smaller batches
2. Use `Split In Batches` node
3. Avoid loading large files entirely
4. Stream data where possible

---

## Quick Debugging Scripts

### debug-last-error.sh
```bash
#!/bin/bash
# Get the last failed execution

LAST_ERROR=$(curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
             "$N8N_API_URL/api/v1/executions?status=error&limit=1")

EXEC_ID=$(echo "$LAST_ERROR" | jq -r '.data[0].id')

if [ "$EXEC_ID" != "null" ]; then
    echo "Last failed execution: $EXEC_ID"
    curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
         "$N8N_API_URL/api/v1/executions/$EXEC_ID" | \
         jq '{
           workflow: .workflowId,
           status: .status,
           lastNode: .data.resultData.lastNodeExecuted,
           error: .data.resultData.error
         }'
else
    echo "No failed executions found"
fi
```

### debug-workflow.sh
```bash
#!/bin/bash
# Debug specific workflow's recent executions
WORKFLOW_ID=$1

echo "Recent executions for workflow $WORKFLOW_ID:"
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
     "$N8N_API_URL/api/v1/executions?workflowId=$WORKFLOW_ID&limit=5" | \
     jq '.data[] | {id, status, startedAt, mode}'
```

---

## Troubleshooting Checklist

### Workflow Won't Start
- [ ] Is workflow activated?
- [ ] Are credentials configured?
- [ ] Does trigger node have correct settings?
- [ ] For webhooks: is the path correct?
- [ ] For schedules: is the cron valid?

### Workflow Fails Silently
- [ ] Check execution logs
- [ ] Verify error handling settings
- [ ] Look for error workflow triggers
- [ ] Check n8n logs: `docker logs n8n`

### Wrong Data Output
- [ ] Add debug nodes at each step
- [ ] Verify expressions with test data
- [ ] Check data types
- [ ] Verify node connections

### Performance Issues
- [ ] Check execution timing
- [ ] Look for slow nodes
- [ ] Consider batching
- [ ] Review API rate limits

---

## Logs and Monitoring

### n8n Server Logs

**Docker:**
```bash
docker logs -f n8n
```

**npm:**
```bash
# Check where n8n logs (varies by setup)
tail -f ~/.n8n/logs/n8n.log
```

### Enable Verbose Logging

Environment variable:
```bash
export N8N_LOG_LEVEL=debug
```

### API for Monitoring

Build a simple monitor:
```bash
#!/bin/bash
# Check for errors every minute

while true; do
    ERROR_COUNT=$(curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
                  "$N8N_API_URL/api/v1/executions?status=error&limit=100" | \
                  jq '.data | length')

    echo "$(date): $ERROR_COUNT errors in last 100 executions"

    if [ "$ERROR_COUNT" -gt 10 ]; then
        echo "WARNING: High error rate!"
        # Send alert
    fi

    sleep 60
done
```
