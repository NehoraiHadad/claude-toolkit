# Claude Toolkit

A collection of skills, subagents, and tools to extend Claude Code capabilities.

## Overview

This repository contains reusable components for Claude Code that reduce token usage, improve efficiency, and provide specialized expertise for various tasks.

## Structure

```
claude-toolkit/
├── skills/              # Claude Code skills
│   └── n8n-expert/      # n8n workflow automation expert
├── subagents/           # Custom subagent configurations (coming soon)
└── tools/               # Helper scripts and utilities (coming soon)
```

## Skills

### n8n-expert

Expert guidance for n8n workflow automation using REST API and CLI. Reduces MCP server dependency by 90%+ through direct API calls and local scripts.

**Features:**
- Complete REST API reference with curl/Python examples
- CLI commands for self-hosted instances
- Workflow patterns and best practices
- Node configuration guides
- Debugging and troubleshooting strategies
- Ready-to-use workflow templates
- Executable scripts for common operations

**Installation:**
```bash
# Copy to Claude skills directory
cp -r skills/n8n-expert ~/.claude/skills/
```

**Environment Setup:**
```bash
export N8N_API_URL="http://localhost:5678"  # Your n8n instance
export N8N_API_KEY="your-api-key"           # From n8n Settings > API
```

**Quick Reference:**
| Operation | Command |
|-----------|---------|
| List workflows | `n8n-api.sh list-workflows` |
| Get workflow | `n8n-api.sh get-workflow <id>` |
| Activate | `n8n-api.sh activate <id>` |
| List executions | `n8n-api.sh list-executions` |
| Debug errors | `execution-manager.py errors` |

[Full documentation](skills/n8n-expert/SKILL.md)

## Installation

### Prerequisites
- Claude Code CLI installed
- Appropriate environment variables configured for each skill

### Installing Skills

Copy the desired skill to your Claude skills directory:

```bash
# Clone this repository
git clone https://github.com/NehoraiHadad/claude-toolkit.git

# Copy a skill
cp -r claude-toolkit/skills/n8n-expert ~/.claude/skills/

# The skill will be automatically activated when relevant topics are mentioned
```

## Usage

Skills are automatically activated based on conversation context. For example, mentioning "n8n", "workflow", or "automation" will activate the n8n-expert skill.

You can also explicitly invoke skills:
```
/skill n8n-expert
```

## Contributing

Feel free to submit issues and pull requests for:
- New skills
- Improvements to existing skills
- Bug fixes
- Documentation updates

## License

MIT License - See [LICENSE](LICENSE) for details.
