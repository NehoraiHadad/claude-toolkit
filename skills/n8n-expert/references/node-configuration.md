# n8n Node Configuration Reference

Detailed configuration guide for the most commonly used n8n nodes.

## Node Naming Convention

All built-in nodes use the prefix `n8n-nodes-base.`:
- `n8n-nodes-base.webhook`
- `n8n-nodes-base.httpRequest`
- `n8n-nodes-base.code`

LangChain/AI nodes use `@n8n/n8n-nodes-langchain.`:
- `@n8n/n8n-nodes-langchain.agent`
- `@n8n/n8n-nodes-langchain.lmChatOpenAi`

---

## Webhook Node

**Type:** `n8n-nodes-base.webhook`
**Version:** 1.1

### Basic Configuration
```json
{
  "type": "n8n-nodes-base.webhook",
  "typeVersion": 1.1,
  "parameters": {
    "httpMethod": "POST",
    "path": "my-webhook",
    "responseMode": "onReceived",
    "options": {}
  }
}
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `httpMethod` | string | GET, POST, PUT, DELETE, PATCH, HEAD |
| `path` | string | URL path after /webhook/ |
| `responseMode` | string | When to send response |
| `options` | object | Additional options |

### Response Modes
- `onReceived` - Respond immediately with default message
- `lastNode` - Respond with last node's output
- `responseNode` - Use "Respond to Webhook" node

### Options
```json
{
  "options": {
    "binaryData": false,
    "ignoreBots": false,
    "noResponseBody": false,
    "rawBody": false,
    "responseCode": 200,
    "responseContentType": "application/json",
    "responseData": ""
  }
}
```

### Full Example
```json
{
  "id": "webhook-1",
  "name": "API Endpoint",
  "type": "n8n-nodes-base.webhook",
  "typeVersion": 1.1,
  "position": [250, 300],
  "parameters": {
    "httpMethod": "POST",
    "path": "api/v1/process",
    "responseMode": "responseNode",
    "options": {
      "rawBody": true
    }
  },
  "webhookId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

## HTTP Request Node

**Type:** `n8n-nodes-base.httpRequest`
**Version:** 4.2

### Basic GET Request
```json
{
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.2,
  "parameters": {
    "url": "https://api.example.com/data",
    "method": "GET",
    "options": {}
  }
}
```

### POST with JSON Body
```json
{
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.2,
  "parameters": {
    "url": "https://api.example.com/submit",
    "method": "POST",
    "sendBody": true,
    "specifyBody": "json",
    "jsonBody": "={{ JSON.stringify({ name: $json.name, email: $json.email }) }}",
    "options": {}
  }
}
```

### With Authentication
```json
{
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.2,
  "parameters": {
    "url": "https://api.example.com/data",
    "method": "GET",
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "httpHeaderAuth",
    "options": {}
  }
}
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | string | Request URL |
| `method` | string | HTTP method |
| `authentication` | string | Auth type |
| `sendBody` | boolean | Include body |
| `sendQuery` | boolean | Include query params |
| `sendHeaders` | boolean | Include custom headers |

### Authentication Types
- `none` - No authentication
- `predefinedCredentialType` - Use stored credentials
- `genericCredentialType` - Generic auth

### Headers Example
```json
{
  "parameters": {
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        {"name": "X-Custom-Header", "value": "custom-value"},
        {"name": "Authorization", "value": "Bearer {{ $json.token }}"}
      ]
    }
  }
}
```

### Query Parameters
```json
{
  "parameters": {
    "sendQuery": true,
    "queryParameters": {
      "parameters": [
        {"name": "page", "value": "{{ $json.page }}"},
        {"name": "limit", "value": "100"}
      ]
    }
  }
}
```

### Full Example with Error Handling
```json
{
  "id": "http-1",
  "name": "Call External API",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.2,
  "position": [450, 300],
  "parameters": {
    "url": "https://api.example.com/v1/data",
    "method": "POST",
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "httpHeaderAuth",
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        {"name": "Content-Type", "value": "application/json"}
      ]
    },
    "sendBody": true,
    "specifyBody": "json",
    "jsonBody": "={{ JSON.stringify($json.payload) }}",
    "options": {
      "timeout": 30000,
      "response": {
        "response": {
          "fullResponse": false
        }
      }
    }
  },
  "onError": "continueErrorOutput"
}
```

---

## Code Node

**Type:** `n8n-nodes-base.code`
**Version:** 2

### JavaScript - All Items at Once
```json
{
  "type": "n8n-nodes-base.code",
  "typeVersion": 2,
  "parameters": {
    "mode": "runOnceForAllItems",
    "jsCode": "// Access all input items\nconst items = $input.all();\n\n// Process items\nconst results = items.map(item => ({\n  json: {\n    ...item.json,\n    processed: true\n  }\n}));\n\nreturn results;"
  }
}
```

### JavaScript - Each Item Separately
```json
{
  "type": "n8n-nodes-base.code",
  "typeVersion": 2,
  "parameters": {
    "mode": "runOnceForEachItem",
    "jsCode": "// Access current item\nconst data = $input.item.json;\n\n// Process and return\nreturn {\n  json: {\n    original: data,\n    doubled: data.value * 2\n  }\n};"
  }
}
```

### Python Mode
```json
{
  "type": "n8n-nodes-base.code",
  "typeVersion": 2,
  "parameters": {
    "mode": "runOnceForAllItems",
    "language": "python",
    "pythonCode": "# Access items\nitems = _input.all()\n\n# Process\nresults = []\nfor item in items:\n    results.append({\n        'json': {\n            **item.json,\n            'processed': True\n        }\n    })\n\nreturn results"
  }
}
```

### Available Variables

**JavaScript:**
- `$input.all()` - All input items
- `$input.first()` - First input item
- `$input.item` - Current item (in forEach mode)
- `$json` - Current item's JSON
- `$binary` - Current item's binary data
- `$env` - Environment variables
- `$workflow` - Workflow info
- `$execution` - Execution info
- `$node` - Node info
- `$prevNode` - Previous node info

**Python:**
- `_input.all()` - All input items
- `_input.first()` - First input item
- `_input.item` - Current item
- `_env` - Environment variables

### Full Example
```json
{
  "id": "code-1",
  "name": "Transform Data",
  "type": "n8n-nodes-base.code",
  "typeVersion": 2,
  "position": [450, 300],
  "parameters": {
    "mode": "runOnceForAllItems",
    "jsCode": "const items = $input.all();\n\nconst transformed = items.map(item => {\n  const { name, email, amount } = item.json;\n  \n  return {\n    json: {\n      fullName: name.toUpperCase(),\n      emailDomain: email.split('@')[1],\n      amountFormatted: `$${amount.toFixed(2)}`,\n      processedAt: new Date().toISOString()\n    }\n  };\n});\n\nreturn transformed;"
  }
}
```

---

## IF Node

**Type:** `n8n-nodes-base.if`
**Version:** 2

### Basic Condition
```json
{
  "type": "n8n-nodes-base.if",
  "typeVersion": 2,
  "parameters": {
    "conditions": {
      "options": {
        "caseSensitive": true,
        "leftValue": "",
        "typeValidation": "strict"
      },
      "conditions": [
        {
          "leftValue": "={{ $json.status }}",
          "rightValue": "active",
          "operator": {
            "type": "string",
            "operation": "equals"
          }
        }
      ],
      "combinator": "and"
    }
  }
}
```

### Multiple Conditions (AND)
```json
{
  "parameters": {
    "conditions": {
      "conditions": [
        {
          "leftValue": "={{ $json.status }}",
          "rightValue": "active",
          "operator": {"type": "string", "operation": "equals"}
        },
        {
          "leftValue": "={{ $json.amount }}",
          "rightValue": "100",
          "operator": {"type": "number", "operation": "gt"}
        }
      ],
      "combinator": "and"
    }
  }
}
```

### Operators

**String Operators:**
- `equals`, `notEquals`
- `contains`, `notContains`
- `startsWith`, `endsWith`
- `isEmpty`, `isNotEmpty`
- `regex`

**Number Operators:**
- `equals`, `notEquals`
- `gt` (>), `gte` (>=)
- `lt` (<), `lte` (<=)

**Boolean Operators:**
- `true`, `false`

**Array Operators:**
- `contains`, `notContains`
- `lengthEquals`, `lengthGt`, `lengthLt`
- `isEmpty`, `isNotEmpty`

### Full Example
```json
{
  "id": "if-1",
  "name": "Check Eligibility",
  "type": "n8n-nodes-base.if",
  "typeVersion": 2,
  "position": [450, 300],
  "parameters": {
    "conditions": {
      "options": {
        "caseSensitive": false,
        "typeValidation": "loose"
      },
      "conditions": [
        {
          "leftValue": "={{ $json.age }}",
          "rightValue": "18",
          "operator": {"type": "number", "operation": "gte"}
        },
        {
          "leftValue": "={{ $json.country }}",
          "rightValue": "US,CA,UK",
          "operator": {"type": "string", "operation": "contains"}
        }
      ],
      "combinator": "and"
    }
  }
}
```

---

## Set Node

**Type:** `n8n-nodes-base.set`
**Version:** 3.4

### Manual Mode - Add Fields
```json
{
  "type": "n8n-nodes-base.set",
  "typeVersion": 3.4,
  "parameters": {
    "mode": "manual",
    "duplicateItem": false,
    "assignments": {
      "assignments": [
        {
          "id": "field1",
          "name": "newField",
          "value": "static value",
          "type": "string"
        },
        {
          "id": "field2",
          "name": "computed",
          "value": "={{ $json.firstName + ' ' + $json.lastName }}",
          "type": "string"
        }
      ]
    },
    "options": {}
  }
}
```

### Raw Mode - Complete JSON
```json
{
  "type": "n8n-nodes-base.set",
  "typeVersion": 3.4,
  "parameters": {
    "mode": "raw",
    "jsonOutput": "={{ { id: $json.id, transformed: true, data: $json } }}"
  }
}
```

### Options
```json
{
  "options": {
    "dotNotation": true,
    "ignoreConversionErrors": false,
    "includeBinary": false
  }
}
```

---

## Merge Node

**Type:** `n8n-nodes-base.merge`
**Version:** 3

### Append Mode
Combines all items from all inputs:
```json
{
  "type": "n8n-nodes-base.merge",
  "typeVersion": 3,
  "parameters": {
    "mode": "append"
  }
}
```

### Combine by Position
Merges items by their index:
```json
{
  "type": "n8n-nodes-base.merge",
  "typeVersion": 3,
  "parameters": {
    "mode": "combine",
    "combineBy": "combineByPosition",
    "options": {}
  }
}
```

### Combine by Fields
Merges items matching on specific fields:
```json
{
  "type": "n8n-nodes-base.merge",
  "typeVersion": 3,
  "parameters": {
    "mode": "combine",
    "combineBy": "combineByFields",
    "fieldsToMatchOn": ["id"],
    "options": {}
  }
}
```

### Choose Branch
Wait for both inputs, output from chosen branch:
```json
{
  "type": "n8n-nodes-base.merge",
  "typeVersion": 3,
  "parameters": {
    "mode": "chooseBranch",
    "chooseBranch": "input1"
  }
}
```

---

## Schedule Trigger Node

**Type:** `n8n-nodes-base.scheduleTrigger`
**Version:** 1.2

### Cron Expression
```json
{
  "type": "n8n-nodes-base.scheduleTrigger",
  "typeVersion": 1.2,
  "parameters": {
    "rule": {
      "interval": [
        {
          "field": "cronExpression",
          "expression": "0 9 * * 1-5"
        }
      ]
    }
  }
}
```

### Interval-based
```json
{
  "type": "n8n-nodes-base.scheduleTrigger",
  "typeVersion": 1.2,
  "parameters": {
    "rule": {
      "interval": [
        {
          "field": "hours",
          "hoursInterval": 4
        }
      ]
    }
  }
}
```

### Common Cron Patterns

| Expression | Description |
|------------|-------------|
| `* * * * *` | Every minute |
| `*/5 * * * *` | Every 5 minutes |
| `0 * * * *` | Every hour |
| `0 9 * * *` | Daily at 9 AM |
| `0 9 * * 1-5` | Weekdays at 9 AM |
| `0 0 * * 0` | Weekly on Sunday |
| `0 0 1 * *` | First of month |

---

## Respond to Webhook Node

**Type:** `n8n-nodes-base.respondToWebhook`
**Version:** 1.1

### JSON Response
```json
{
  "type": "n8n-nodes-base.respondToWebhook",
  "typeVersion": 1.1,
  "parameters": {
    "respondWith": "json",
    "responseBody": "={{ $json }}",
    "options": {}
  }
}
```

### Custom Response
```json
{
  "type": "n8n-nodes-base.respondToWebhook",
  "typeVersion": 1.1,
  "parameters": {
    "respondWith": "json",
    "responseBody": "={\"success\": true, \"data\": {{ JSON.stringify($json) }}}",
    "options": {
      "responseCode": 200,
      "responseHeaders": {
        "entries": [
          {"name": "X-Custom-Header", "value": "custom"}
        ]
      }
    }
  }
}
```

### Error Response
```json
{
  "type": "n8n-nodes-base.respondToWebhook",
  "typeVersion": 1.1,
  "parameters": {
    "respondWith": "json",
    "responseBody": "={\"success\": false, \"error\": \"{{ $json.errorMessage }}\"}",
    "options": {
      "responseCode": 400
    }
  }
}
```

---

## Expression Reference

### Accessing Data
```javascript
// Current item JSON
$json.fieldName
$json['field-with-dash']
$json.nested.field

// Previous node data
$('Node Name').item.json.field

// All items from node
$('Node Name').all()

// First item from node
$('Node Name').first().json

// Environment variable
$env.MY_VAR

// Workflow info
$workflow.name
$workflow.id
$workflow.active

// Execution info
$execution.id
$execution.mode
$execution.resumeUrl
```

### Utility Functions
```javascript
// Date/Time
$now                    // Current DateTime
$today                  // Today's date
$now.toISO()           // ISO string

// JSON
JSON.stringify(obj)
JSON.parse(str)

// String manipulation
$json.text.toLowerCase()
$json.text.toUpperCase()
$json.text.trim()
$json.text.split(',')

// Math
Math.round($json.value)
Math.floor($json.value)
Math.ceil($json.value)
Number($json.stringValue)
```
