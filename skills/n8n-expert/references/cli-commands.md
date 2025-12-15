# n8n CLI Commands Reference

The n8n CLI is available for self-hosted instances. Commands operate directly on the n8n database.

## Prerequisites

- n8n installed via npm: `npm install -g n8n`
- Or running in Docker with exec access
- Commands run on the same machine as n8n

## Important Notes

- CLI commands operate on the database directly
- Changes take effect after n8n restart (for some commands)
- Always backup before major operations
- Use `--help` with any command for options

---

## Workflow Commands

### Export Workflows

Export all workflows to JSON files:
```bash
n8n export:workflow --all --output=./workflows/
```

Export specific workflow by ID:
```bash
n8n export:workflow --id=1 --output=workflow.json
```

Export with pretty formatting:
```bash
n8n export:workflow --all --output=./workflows/ --pretty
```

**Options:**
- `--all`: Export all workflows
- `--id=<id>`: Export specific workflow
- `--output=<path>`: Output file or directory
- `--pretty`: Pretty print JSON
- `--separate`: Each workflow in separate file (with --all)

### Import Workflows

Import from JSON file:
```bash
n8n import:workflow --input=workflow.json
```

Import all from directory:
```bash
n8n import:workflow --input=./workflows/
```

**Options:**
- `--input=<path>`: Input file or directory
- `--separate`: Import from separate files

---

## Credential Commands

### Export Credentials

Export all credentials:
```bash
n8n export:credentials --all --output=./credentials/
```

Export specific credential:
```bash
n8n export:credentials --id=1 --output=cred.json
```

**Options:**
- `--all`: Export all credentials
- `--id=<id>`: Export specific credential
- `--output=<path>`: Output path
- `--decrypted`: Include decrypted secrets (CAUTION!)
- `--pretty`: Pretty print JSON

**Security Note:** Credentials are encrypted by default. Use `--decrypted` only when needed and protect the output.

### Import Credentials

Import credentials:
```bash
n8n import:credentials --input=cred.json
```

**Options:**
- `--input=<path>`: Input file or directory
- `--separate`: Import from separate files

---

## Execution Commands

### Execute Workflow

Run workflow by ID:
```bash
n8n execute --id=1
```

Run with specific data:
```bash
n8n execute --id=1 --rawBody='{"key": "value"}'
```

**Options:**
- `--id=<id>`: Workflow ID to execute
- `--rawBody=<json>`: Input data as JSON string
- `--file=<path>`: Input data from file

### List Executions

Not available via CLI - use REST API instead.

---

## User Management Commands

### Reset User Management

Reset to initial setup state (removes all users):
```bash
n8n user-management:reset
```

**Warning:** This removes ALL user accounts. Use with caution.

---

## Security Commands

### Security Audit

Run security audit on instance:
```bash
n8n audit
```

Checks for:
- Workflows with risky configurations
- Credentials security issues
- Potentially dangerous nodes
- Best practice violations

---

## Database Commands

### Update Database Schema

Run database migrations:
```bash
n8n db:update
```

Usually runs automatically on startup.

---

## License Commands (Enterprise)

### Activate License

```bash
n8n license:activate --key=<license-key>
```

### Clear License

```bash
n8n license:clear
```

---

## Environment Variables

Control CLI behavior with environment variables:

```bash
# Database connection
export DB_TYPE=postgresdb
export DB_POSTGRESDB_HOST=localhost
export DB_POSTGRESDB_PORT=5432
export DB_POSTGRESDB_DATABASE=n8n
export DB_POSTGRESDB_USER=n8n
export DB_POSTGRESDB_PASSWORD=secret

# Or use SQLite (default)
export DB_TYPE=sqlite
export DB_SQLITE_DATABASE=/data/database.sqlite

# Encryption key (required for credential export/import)
export N8N_ENCRYPTION_KEY=your-encryption-key
```

---

## Docker Execution

When n8n runs in Docker, execute CLI commands via docker exec:

```bash
# List containers
docker ps | grep n8n

# Execute CLI command
docker exec -it n8n_container n8n export:workflow --all --output=/data/export/
```

With docker-compose:
```bash
docker-compose exec n8n n8n export:workflow --all --output=/data/export/
```

---

## Common Workflows

### Backup All Workflows and Credentials

```bash
#!/bin/bash
BACKUP_DIR="./backup-$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Export workflows
n8n export:workflow --all --output="$BACKUP_DIR/workflows/" --pretty --separate

# Export credentials (encrypted)
n8n export:credentials --all --output="$BACKUP_DIR/credentials/" --separate

echo "Backup complete: $BACKUP_DIR"
```

### Restore from Backup

```bash
#!/bin/bash
BACKUP_DIR="./backup-20240120"

# Import credentials first (workflows may reference them)
n8n import:credentials --input="$BACKUP_DIR/credentials/" --separate

# Import workflows
n8n import:workflow --input="$BACKUP_DIR/workflows/" --separate

# Restart n8n to apply changes
# systemctl restart n8n  # or docker restart n8n
```

### Export Single Workflow to Share

```bash
# Get workflow ID from n8n UI or API
WORKFLOW_ID=5

# Export with pretty formatting
n8n export:workflow --id=$WORKFLOW_ID --output=shared-workflow.json --pretty

# Remove sensitive data if needed
jq 'del(.credentials)' shared-workflow.json > shared-workflow-clean.json
```

### Migrate Workflows Between Instances

```bash
# On source instance
n8n export:workflow --all --output=./migration/ --separate

# Copy files to target
scp -r ./migration/ user@target:/tmp/

# On target instance
n8n import:workflow --input=/tmp/migration/ --separate
```

---

## Troubleshooting CLI

### Command Not Found

```bash
# Check n8n is installed
which n8n

# If using npm global
npm list -g n8n

# Reinstall if needed
npm install -g n8n
```

### Database Connection Issues

```bash
# Check environment variables
echo $DB_TYPE
echo $DB_POSTGRESDB_HOST

# Test connection
n8n db:update  # Should succeed if connection works
```

### Encryption Key Missing

```bash
# Error: Encryption key not set
export N8N_ENCRYPTION_KEY=your-key-here

# The key should match your running n8n instance
```

### Permission Denied

```bash
# If running as different user
sudo -u n8n n8n export:workflow --all --output=./export/

# Or fix permissions
chown -R $(whoami) ./export/
```

---

## CLI vs REST API

| Operation | CLI | REST API |
|-----------|-----|----------|
| Export workflows | Yes | Yes (via GET) |
| Import workflows | Yes | Yes (via POST) |
| Execute workflow | Yes | Yes (webhooks) |
| List workflows | No | Yes |
| Activate/Deactivate | No | Yes |
| View executions | No | Yes |
| User management | Limited | Yes |
| Backup/Restore | Excellent | Possible |
| Bulk operations | Good | Good |

**Recommendation:** Use CLI for backup/restore/migration. Use REST API for runtime operations.
