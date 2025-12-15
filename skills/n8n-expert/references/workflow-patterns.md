# n8n Workflow Patterns Reference

Common patterns and structures for building effective n8n workflows.

## Workflow Structure Basics

### Minimal Workflow Structure
```json
{
  "name": "Workflow Name",
  "nodes": [],
  "connections": {},
  "settings": {
    "executionOrder": "v1"
  }
}
```

### Node Structure
```json
{
  "id": "unique-uuid",
  "name": "Display Name",
  "type": "n8n-nodes-base.nodeType",
  "typeVersion": 1,
  "position": [x, y],
  "parameters": {}
}
```

### Connection Structure
```json
{
  "connections": {
    "Source Node Name": {
      "main": [
        [
          {
            "node": "Target Node Name",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

---

## Trigger Patterns

### Webhook Trigger
```json
{
  "id": "webhook-1",
  "name": "Webhook",
  "type": "n8n-nodes-base.webhook",
  "typeVersion": 1.1,
  "position": [250, 300],
  "parameters": {
    "httpMethod": "POST",
    "path": "my-endpoint",
    "responseMode": "responseNode",
    "options": {}
  },
  "webhookId": "unique-webhook-id"
}
```

**Webhook Response Modes:**
- `onReceived`: Respond immediately
- `lastNode`: Respond with last node output
- `responseNode`: Use "Respond to Webhook" node

### Schedule Trigger
```json
{
  "id": "schedule-1",
  "name": "Schedule Trigger",
  "type": "n8n-nodes-base.scheduleTrigger",
  "typeVersion": 1.2,
  "position": [250, 300],
  "parameters": {
    "rule": {
      "interval": [
        {
          "field": "cronExpression",
          "expression": "0 9 * * *"
        }
      ]
    }
  }
}
```

**Common Cron Expressions:**
- `0 * * * *` - Every hour
- `0 9 * * *` - Daily at 9 AM
- `0 9 * * 1` - Every Monday at 9 AM
- `*/15 * * * *` - Every 15 minutes
- `0 0 1 * *` - First day of month

### Manual Trigger
```json
{
  "id": "manual-1",
  "name": "Manual Trigger",
  "type": "n8n-nodes-base.manualTrigger",
  "typeVersion": 1,
  "position": [250, 300],
  "parameters": {}
}
```

---

## Data Processing Patterns

### Transform Data with Set Node
```json
{
  "id": "set-1",
  "name": "Transform Data",
  "type": "n8n-nodes-base.set",
  "typeVersion": 3.4,
  "position": [450, 300],
  "parameters": {
    "mode": "manual",
    "duplicateItem": false,
    "assignments": {
      "assignments": [
        {
          "name": "newField",
          "value": "={{ $json.existingField }}",
          "type": "string"
        },
        {
          "name": "computed",
          "value": "={{ $json.price * $json.quantity }}",
          "type": "number"
        }
      ]
    }
  }
}
```

### Filter with IF Node
```json
{
  "id": "if-1",
  "name": "Check Condition",
  "type": "n8n-nodes-base.if",
  "typeVersion": 2,
  "position": [450, 300],
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

**IF Node Outputs:**
- `main[0]` - True branch
- `main[1]` - False branch

### Code Node (JavaScript)
```json
{
  "id": "code-1",
  "name": "Process Data",
  "type": "n8n-nodes-base.code",
  "typeVersion": 2,
  "position": [450, 300],
  "parameters": {
    "mode": "runOnceForAllItems",
    "jsCode": "// Access all items\nconst items = $input.all();\n\n// Process and return\nreturn items.map(item => ({\n  json: {\n    ...item.json,\n    processed: true,\n    timestamp: new Date().toISOString()\n  }\n}));"
  }
}
```

**Code Node Modes:**
- `runOnceForAllItems` - Run once, access all items
- `runOnceForEachItem` - Run for each item separately

---

## Branching Patterns

### Parallel Execution
Connect one node to multiple targets:
```json
{
  "connections": {
    "Start Node": {
      "main": [
        [
          {"node": "Branch A", "type": "main", "index": 0},
          {"node": "Branch B", "type": "main", "index": 0},
          {"node": "Branch C", "type": "main", "index": 0}
        ]
      ]
    }
  }
}
```

### Merge Branches
```json
{
  "id": "merge-1",
  "name": "Merge Results",
  "type": "n8n-nodes-base.merge",
  "typeVersion": 3,
  "position": [850, 300],
  "parameters": {
    "mode": "combine",
    "combineBy": "combineByPosition",
    "options": {}
  }
}
```

**Merge Modes:**
- `append` - Combine all items
- `combine` - Match items by position
- `multiplex` - Create all combinations
- `chooseBranch` - Wait for both, use one

### Switch Node (Multiple Conditions)
```json
{
  "id": "switch-1",
  "name": "Route by Type",
  "type": "n8n-nodes-base.switch",
  "typeVersion": 3,
  "position": [450, 300],
  "parameters": {
    "rules": {
      "rules": [
        {
          "outputKey": "order",
          "conditions": {
            "conditions": [
              {
                "leftValue": "={{ $json.type }}",
                "rightValue": "order",
                "operator": {"type": "string", "operation": "equals"}
              }
            ]
          }
        },
        {
          "outputKey": "refund",
          "conditions": {
            "conditions": [
              {
                "leftValue": "={{ $json.type }}",
                "rightValue": "refund",
                "operator": {"type": "string", "operation": "equals"}
              }
            ]
          }
        }
      ]
    },
    "options": {
      "fallbackOutput": "extra"
    }
  }
}
```

---

## Loop Patterns

### Split in Batches
Process items in chunks:
```json
{
  "id": "batch-1",
  "name": "Split In Batches",
  "type": "n8n-nodes-base.splitInBatches",
  "typeVersion": 3,
  "position": [450, 300],
  "parameters": {
    "batchSize": 10,
    "options": {}
  }
}
```

**Connections for loop:**
```json
{
  "Split In Batches": {
    "main": [
      [{"node": "Process Batch", "type": "main", "index": 0}]
    ]
  },
  "Process Batch": {
    "main": [
      [{"node": "Split In Batches", "type": "main", "index": 0}]
    ]
  }
}
```

### Loop Over Items
```json
{
  "id": "loop-1",
  "name": "Loop Over Items",
  "type": "n8n-nodes-base.splitInBatches",
  "typeVersion": 3,
  "position": [450, 300],
  "parameters": {
    "batchSize": 1,
    "options": {
      "reset": false
    }
  }
}
```

---

## Error Handling Patterns

### Continue on Fail
```json
{
  "id": "http-1",
  "name": "HTTP Request",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.2,
  "position": [450, 300],
  "parameters": {...},
  "onError": "continueRegularOutput"
}
```

**onError Options:**
- `stopWorkflow` - Stop on error (default)
- `continueRegularOutput` - Continue, error in output
- `continueErrorOutput` - Route to error output

### Error Branch
```json
{
  "id": "http-1",
  "name": "HTTP Request",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.2,
  "position": [450, 300],
  "parameters": {...},
  "onError": "continueErrorOutput"
}
```

**Connections with error handling:**
```json
{
  "HTTP Request": {
    "main": [
      [{"node": "Success Handler", "type": "main", "index": 0}]
    ],
    "error": [
      [{"node": "Error Handler", "type": "main", "index": 0}]
    ]
  }
}
```

### Error Workflow (Global)
Set in workflow settings:
```json
{
  "settings": {
    "errorWorkflow": "error-handler-workflow-id"
  }
}
```

---

## HTTP Request Patterns

### GET Request
```json
{
  "id": "http-1",
  "name": "Get Data",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.2,
  "position": [450, 300],
  "parameters": {
    "url": "https://api.example.com/data",
    "method": "GET",
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "httpHeaderAuth",
    "options": {}
  }
}
```

### POST with JSON Body
```json
{
  "id": "http-1",
  "name": "Send Data",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.2,
  "position": [450, 300],
  "parameters": {
    "url": "https://api.example.com/submit",
    "method": "POST",
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        {"name": "field1", "value": "={{ $json.value1 }}"},
        {"name": "field2", "value": "={{ $json.value2 }}"}
      ]
    },
    "options": {}
  }
}
```

### Pagination Loop
```json
{
  "id": "http-1",
  "name": "Paginated Request",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.2,
  "position": [450, 300],
  "parameters": {
    "url": "https://api.example.com/items",
    "method": "GET",
    "options": {
      "pagination": {
        "paginationMode": "off"
      }
    }
  }
}
```

---

## Webhook Response Pattern

### Respond to Webhook
```json
{
  "id": "respond-1",
  "name": "Respond",
  "type": "n8n-nodes-base.respondToWebhook",
  "typeVersion": 1.1,
  "position": [850, 300],
  "parameters": {
    "respondWith": "json",
    "responseBody": "={{ $json }}",
    "options": {
      "responseCode": 200,
      "responseHeaders": {
        "entries": [
          {"name": "Content-Type", "value": "application/json"}
        ]
      }
    }
  }
}
```

---

## AI/LangChain Patterns

### Basic AI Agent
```json
{
  "nodes": [
    {
      "id": "agent-1",
      "name": "AI Agent",
      "type": "@n8n/n8n-nodes-langchain.agent",
      "typeVersion": 1.6,
      "position": [450, 300],
      "parameters": {
        "options": {}
      }
    },
    {
      "id": "model-1",
      "name": "OpenAI Chat Model",
      "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
      "typeVersion": 1,
      "position": [250, 500],
      "parameters": {
        "model": "gpt-4o-mini"
      }
    }
  ],
  "connections": {
    "OpenAI Chat Model": {
      "ai_languageModel": [
        [{"node": "AI Agent", "type": "ai_languageModel", "index": 0}]
      ]
    }
  }
}
```

**AI Connection Types:**
- `ai_languageModel` - Language model
- `ai_tool` - Agent tools
- `ai_memory` - Conversation memory
- `ai_embedding` - Embedding model
- `ai_vectorStore` - Vector store

---

## Complete Example: API Processing Workflow

```json
{
  "name": "API Data Processing",
  "nodes": [
    {
      "id": "webhook-1",
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1.1,
      "position": [250, 300],
      "parameters": {
        "httpMethod": "POST",
        "path": "process-data",
        "responseMode": "responseNode"
      }
    },
    {
      "id": "if-1",
      "name": "Validate Input",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [450, 300],
      "parameters": {
        "conditions": {
          "conditions": [
            {
              "leftValue": "={{ $json.body.data }}",
              "rightValue": "",
              "operator": {"type": "string", "operation": "notEmpty"}
            }
          ]
        }
      }
    },
    {
      "id": "http-1",
      "name": "External API",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [650, 200],
      "parameters": {
        "url": "https://api.example.com/process",
        "method": "POST",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {"name": "input", "value": "={{ $json.body.data }}"}
          ]
        }
      },
      "onError": "continueErrorOutput"
    },
    {
      "id": "respond-success",
      "name": "Success Response",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1.1,
      "position": [850, 150],
      "parameters": {
        "respondWith": "json",
        "responseBody": "={\"success\": true, \"data\": {{ $json }}}"
      }
    },
    {
      "id": "respond-error",
      "name": "Error Response",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1.1,
      "position": [850, 400],
      "parameters": {
        "respondWith": "json",
        "responseBody": "={\"success\": false, \"error\": \"Processing failed\"}",
        "options": {"responseCode": 500}
      }
    }
  ],
  "connections": {
    "Webhook": {
      "main": [[{"node": "Validate Input", "type": "main", "index": 0}]]
    },
    "Validate Input": {
      "main": [
        [{"node": "External API", "type": "main", "index": 0}],
        [{"node": "Error Response", "type": "main", "index": 0}]
      ]
    },
    "External API": {
      "main": [[{"node": "Success Response", "type": "main", "index": 0}]],
      "error": [[{"node": "Error Response", "type": "main", "index": 0}]]
    }
  },
  "settings": {"executionOrder": "v1"}
}
```
