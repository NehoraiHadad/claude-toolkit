# n8n REST API Complete Reference

> **Important:** n8n has two REST APIs:
> - `/api/v1/` - **Public API** (documented here, recommended for external integrations)
> - `/rest/` - Internal API (for embedded use, less stable)
>
> Always use the Public API (`/api/v1/`) for scripts and automation.

## Authentication

All API requests require the `X-N8N-API-KEY` header.

### Getting Your API Key
1. Open n8n UI
2. Go to Settings > API
3. Generate new API key
4. Store securely (only shown once)

### Request Format
```bash
curl -H "X-N8N-API-KEY: $N8N_API_KEY" \
     -H "Content-Type: application/json" \
     "$N8N_API_URL/api/v1/endpoint"
```

## Base URL

```
http://localhost:5678/api/v1/
```

For cloud: `https://your-instance.app.n8n.cloud/api/v1/`

---

## Workflow Endpoints

### List All Workflows
```bash
GET /api/v1/workflows
```

**Query Parameters:**
- `limit` (int): Max results (default 100)
- `cursor` (string): Pagination cursor
- `active` (boolean): Filter by active status
- `tags` (string): Filter by tag name

**Example:**
```bash
# List all workflows
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
     "$N8N_API_URL/api/v1/workflows" | jq '.data'

# List only active workflows
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
     "$N8N_API_URL/api/v1/workflows?active=true"

# With pagination
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
     "$N8N_API_URL/api/v1/workflows?limit=10"
```

**Response:**
```json
{
  "data": [
    {
      "id": "1",
      "name": "My Workflow",
      "active": true,
      "createdAt": "2024-01-15T10:30:00.000Z",
      "updatedAt": "2024-01-20T14:22:00.000Z",
      "tags": []
    }
  ],
  "nextCursor": "eyJsYXN0SWQiOiIxMCJ9"
}
```

### Get Single Workflow
```bash
GET /api/v1/workflows/{id}
```

**Example:**
```bash
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
     "$N8N_API_URL/api/v1/workflows/1" | jq
```

**Response:**
```json
{
  "id": "1",
  "name": "My Workflow",
  "active": true,
  "nodes": [...],
  "connections": {...},
  "settings": {...},
  "staticData": null,
  "createdAt": "2024-01-15T10:30:00.000Z",
  "updatedAt": "2024-01-20T14:22:00.000Z"
}
```

### Create Workflow
```bash
POST /api/v1/workflows
```

**Request Body:**
```json
{
  "name": "New Workflow",
  "nodes": [
    {
      "id": "node-1",
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [250, 300],
      "parameters": {
        "httpMethod": "POST",
        "path": "my-webhook"
      }
    }
  ],
  "connections": {},
  "settings": {
    "executionOrder": "v1"
  }
}
```

**Example:**
```bash
curl -s -X POST \
     -H "X-N8N-API-KEY: $N8N_API_KEY" \
     -H "Content-Type: application/json" \
     -d @workflow.json \
     "$N8N_API_URL/api/v1/workflows"
```

### Update Workflow
```bash
PUT /api/v1/workflows/{id}
```

**Example:**
```bash
# Get workflow, modify, update
WORKFLOW=$(curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
           "$N8N_API_URL/api/v1/workflows/1")

# Modify in jq and update
echo "$WORKFLOW" | jq '.name = "Updated Name"' | \
curl -s -X PUT \
     -H "X-N8N-API-KEY: $N8N_API_KEY" \
     -H "Content-Type: application/json" \
     -d @- \
     "$N8N_API_URL/api/v1/workflows/1"
```

### Delete Workflow
```bash
DELETE /api/v1/workflows/{id}
```

**Example:**
```bash
curl -s -X DELETE \
     -H "X-N8N-API-KEY: $N8N_API_KEY" \
     "$N8N_API_URL/api/v1/workflows/1"
```

### Activate Workflow
```bash
POST /api/v1/workflows/{id}/activate
```

**Example:**
```bash
curl -s -X POST \
     -H "X-N8N-API-KEY: $N8N_API_KEY" \
     "$N8N_API_URL/api/v1/workflows/1/activate"
```

### Deactivate Workflow
```bash
POST /api/v1/workflows/{id}/deactivate
```

**Example:**
```bash
curl -s -X POST \
     -H "X-N8N-API-KEY: $N8N_API_KEY" \
     "$N8N_API_URL/api/v1/workflows/1/deactivate"
```

---

## Execution Endpoints

### List Executions
```bash
GET /api/v1/executions
```

**Query Parameters:**
- `limit` (int): Max results (default 20)
- `cursor` (string): Pagination cursor
- `status` (string): `success`, `error`, `waiting`
- `workflowId` (string): Filter by workflow

**Example:**
```bash
# Recent executions
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
     "$N8N_API_URL/api/v1/executions?limit=10" | jq '.data'

# Failed executions only
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
     "$N8N_API_URL/api/v1/executions?status=error&limit=5"

# For specific workflow
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
     "$N8N_API_URL/api/v1/executions?workflowId=1"
```

**Response:**
```json
{
  "data": [
    {
      "id": "123",
      "workflowId": "1",
      "status": "success",
      "startedAt": "2024-01-20T10:00:00.000Z",
      "stoppedAt": "2024-01-20T10:00:05.000Z",
      "mode": "webhook"
    }
  ],
  "nextCursor": "..."
}
```

### Get Execution Details
```bash
GET /api/v1/executions/{id}
```

**Query Parameters:**
- `includeData` (boolean): Include full execution data (default true)

**Example:**
```bash
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
     "$N8N_API_URL/api/v1/executions/123" | jq
```

**Response with data:**
```json
{
  "id": "123",
  "workflowId": "1",
  "status": "success",
  "data": {
    "resultData": {
      "runData": {
        "Webhook": [{
          "startTime": 1705746000000,
          "executionTime": 5,
          "data": {
            "main": [[{"json": {"body": "..."}}]]
          }
        }]
      }
    }
  }
}
```

### Delete Execution
```bash
DELETE /api/v1/executions/{id}
```

**Example:**
```bash
curl -s -X DELETE \
     -H "X-N8N-API-KEY: $N8N_API_KEY" \
     "$N8N_API_URL/api/v1/executions/123"
```

---

## Webhook Endpoints

### Production Webhook
```bash
POST /webhook/{path}
```

Triggers active workflow with webhook node.

**Example:**
```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello", "data": {"key": "value"}}' \
     "$N8N_API_URL/webhook/my-webhook-path"
```

### Test Webhook
```bash
POST /webhook-test/{path}
```

Triggers workflow in test mode (visible in editor).

**Example:**
```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"test": true}' \
     "$N8N_API_URL/webhook-test/my-webhook-path"
```

---

## Credential Endpoints

### List Credentials
```bash
GET /api/v1/credentials
```

**Example:**
```bash
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
     "$N8N_API_URL/api/v1/credentials" | jq '.data'
```

**Note:** Credential data (secrets) are not returned via API for security.

### Get Credential Schema
```bash
GET /api/v1/credentials/schema/{credentialTypeName}
```

**Example:**
```bash
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
     "$N8N_API_URL/api/v1/credentials/schema/slackApi"
```

---

## Tags Endpoints

### List Tags
```bash
GET /api/v1/tags
```

### Create Tag
```bash
POST /api/v1/tags
```

**Body:**
```json
{"name": "production"}
```

---

## Python Examples

### Using requests library

```python
import requests
import os

N8N_URL = os.getenv('N8N_API_URL', 'http://localhost:5678')
API_KEY = os.getenv('N8N_API_KEY')

headers = {
    'X-N8N-API-KEY': API_KEY,
    'Content-Type': 'application/json'
}

# List workflows
response = requests.get(f'{N8N_URL}/api/v1/workflows', headers=headers)
workflows = response.json()['data']

# Get specific workflow
workflow = requests.get(
    f'{N8N_URL}/api/v1/workflows/1',
    headers=headers
).json()

# Create workflow
new_workflow = {
    'name': 'API Created Workflow',
    'nodes': [],
    'connections': {},
    'settings': {'executionOrder': 'v1'}
}
response = requests.post(
    f'{N8N_URL}/api/v1/workflows',
    headers=headers,
    json=new_workflow
)

# Activate workflow
requests.post(
    f'{N8N_URL}/api/v1/workflows/1/activate',
    headers=headers
)

# Trigger webhook
requests.post(
    f'{N8N_URL}/webhook/my-path',
    json={'data': 'test'}
)

# Get failed executions
failed = requests.get(
    f'{N8N_URL}/api/v1/executions',
    headers=headers,
    params={'status': 'error', 'limit': 10}
).json()['data']
```

---

## Error Responses

### 401 Unauthorized
```json
{"message": "Unauthorized"}
```
Check API key is correct.

### 404 Not Found
```json
{"message": "Not Found"}
```
Resource doesn't exist.

### 400 Bad Request
```json
{"message": "Validation error", "errors": [...]}
```
Invalid request body/parameters.

### 409 Conflict
```json
{"message": "Workflow is active"}
```
Cannot delete active workflow.

---

## Rate Limiting

Self-hosted: No rate limits by default.
Cloud: Check your plan limits.

## Pagination Pattern

```bash
# First page
RESPONSE=$(curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
           "$N8N_API_URL/api/v1/workflows?limit=10")

# Get cursor for next page
CURSOR=$(echo "$RESPONSE" | jq -r '.nextCursor')

# Next page
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
     "$N8N_API_URL/api/v1/workflows?limit=10&cursor=$CURSOR"
```

---

## API Playground

Access interactive API docs at:
```
http://localhost:5678/api/v1/docs
```

Swagger UI for testing endpoints directly.
