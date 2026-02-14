# HTB Command Automation Tool

A CLI-based command reference and generation tool for penetration testing with user-friendly interactive interface.

## Features

- Store and manage commands for multiple pentesting tools (nmap, smb-client, netcat, etc.)
- **Flows**: Multi-step workflows (e.g. SMB enumeration, nmap recon) — generate bash/Python scripts from command sequences
- Interactive CLI for easy command addition and management
- Tool categorization for better organization
- Copy-to-clipboard functionality for seamless workflow
- YAML-based storage for easy version control
- Modular architecture for adding new tools

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd htb-automations

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Quick Start

```bash
# Add a new command (interactive)
htb add

# List all commands
htb list

# Search for commands
htb search "version detection"

# Generate a command with parameters
htb gen nmap:basic-scan -p target=10.10.10.5

# List flows and generate a script from a flow
htb flow list
htb flow gen smb-enumeration --param target=10.10.10.5 --save enum.sh
```

## Project Structure

- `src/core/` - Core components (Command, BaseTool, Storage, CommandManager, Flow, FlowManager)
- `src/tools/` - Concrete tool implementations
- `src/cli/` - CLI interface and commands
- `data/commands/` - YAML command database
- `data/flows/` - Flow definitions (multi-step workflows)
- `config.yaml` - Configuration file

## Flows

Flows are sequences of commands that you can run as a single script. The tool **generates** bash or Python scripts; it does not execute them.

- `htb flow list` — List flows (optionally filter by `--tag`)
- `htb flow show <flow-id>` — Show flow details
- `htb flow gen <flow-id> --param target=IP [--save script.sh]` — Generate script (use `--preview` for commands only)
- `htb flow add` — Create a flow interactively
- `htb flow edit/delete/search` — Manage flows

Example flows are in `data/flows/` (e.g. `smb-enumeration`, `nmap-quick-recon`). See [specs/FLOWS_SPEC.md](specs/FLOWS_SPEC.md) for the full specification.

## Example Workflow

See [docs/WORKFLOW.md](docs/WORKFLOW.md) for a typical pentesting workflow and usage examples.

## Development Status

**Current Phase:** Phase 6 - Polish & Documentation

See [specs/SPEC.md](specs/SPEC.md) for the technical specification and [specs/FLOWS_SPEC.md](specs/FLOWS_SPEC.md) for the flows feature.

## License

MIT License
