# HTB Command Automation Tool

A CLI-based command reference and generation tool for penetration testing with user-friendly interactive interface.

## Features

- Store and manage commands for multiple pentesting tools (nmap, smb-client, netcat, etc.)
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
```

## Project Structure

- `src/core/` - Core components (Command, BaseTool, Storage, CommandManager)
- `src/tools/` - Concrete tool implementations
- `src/cli/` - CLI interface and commands
- `data/commands/` - YAML command database
- `config.yaml` - Configuration file

## Example Workflow

See [docs/WORKFLOW.md](docs/WORKFLOW.md) for a typical pentesting workflow and usage examples.

## Development Status

**Current Phase:** Phase 6 - Polish & Documentation

See [SPEC.md](SPEC.md) for detailed technical specification.

## License

MIT License
