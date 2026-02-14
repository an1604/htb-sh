# HTB Command Automation Tool

[![Tests](https://github.com/yourusername/htb-automations/actions/workflows/test.yml/badge.svg)](https://github.com/yourusername/htb-automations/actions/workflows/test.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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

## Usage Examples

### Managing Tools

**Interactive Mode** (prompts for all inputs):
```bash
htb tool add
```

**Quick Mode** (provide all details):
```bash
htb tool add gobuster -d "Directory brute-forcing tool" -c web
```

**List all tools**:
```bash
htb tool list
htb tool list --category reconnaissance
```

### Adding Commands

**Fully Interactive** (7-step wizard):
```bash
htb add
```

**Semi-Interactive** (pre-select tool):
```bash
htb add nmap
```

**Quick Mode** (all details provided):
```bash
htb add nmap \
  --id quick-scan \
  --name "Quick Scan" \
  --cmd "nmap -sV {target}" \
  --explain "Fast service version detection" \
  --param "target:Target IP address:required" \
  --tag "scanning,quick"
```

### Generating Commands

**Interactive** (prompts for parameters):
```bash
htb gen nmap:basic-scan
```

**Direct** (all parameters provided):
```bash
htb gen nmap:basic-scan -p target=10.10.10.5
```

**Multiple Parameters**:
```bash
htb gen nmap:complex-scan \
  -p target=10.10.10.5 \
  -p ports="-p 80,443,8080" \
  -p options="-sV -sC"
```

**Output Options**:
```bash
# Don't copy to clipboard
htb gen nmap:basic-scan -p target=10.10.10.5 --no-copy

# Print only (minimal output)
htb gen nmap:basic-scan -p target=10.10.10.5 --print-only
```

### Managing Commands

```bash
# List all commands
htb list

# Filter by tool
htb list --tool nmap

# Filter by tag
htb list --tag aggressive

# Search commands
htb search "version detection"

# Show command details
htb show nmap:basic-scan

# Edit a command
htb edit nmap:basic-scan

# Delete a command
htb delete nmap:basic-scan
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

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ -v --cov=src --cov-report=term-missing

# Run tests excluding CI-skipped tests (same as CI)
pytest tests/ -v -m "not skip_ci"
```

**Note:** Some tests are marked with `@pytest.mark.skip_ci` and are skipped in CI environments due to mocking compatibility issues with Click commands. These tests run successfully in local environments but fail in CI due to environment-specific differences.

### CI/CD

This project uses GitHub Actions for continuous integration. All tests run automatically on:
- Pull requests to `main` or `dev` branches
- Direct pushes to `main` or `dev` branches

Tests run against Python 3.8, 3.9, 3.10, and 3.11. All tests must pass before merging.

See [.github/BRANCH_PROTECTION.md](.github/BRANCH_PROTECTION.md) for recommended branch protection rules.

## Development Status

**Current Phase:** Phase 6 - Polish & Documentation

See [specs/SPEC.md](specs/SPEC.md) for the technical specification and [specs/FLOWS_SPEC.md](specs/FLOWS_SPEC.md) for the flows feature.

## License

MIT License
