# HTB Command Automation Tool - Technical Specification

**Version:** 1.0  
**Date:** February 7, 2026  
**Status:** Approved - Ready for Implementation

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture Design](#architecture-design)
3. [Project Structure](#project-structure)
4. [Core Classes & Interfaces](#core-classes--interfaces)
5. [Interactive CLI Interface](#interactive-cli-interface)
6. [Data Format](#data-format)
7. [Configuration](#configuration)
8. [Dependencies](#dependencies)
9. [Implementation Plan](#implementation-plan)
10. [Key Features](#key-features)
11. [Example Implementations](#example-implementations)

---

## Project Overview

### Purpose
A CLI-based command reference and generation tool for penetration testing, with **user-friendly interactive interface** for managing commands and modular architecture supporting easy addition of new tools.

### Core Requirements
1. Store commands for multiple pentesting tools (nmap, smb-client, netcat, etc.)
2. Each command includes: the command itself, explanation, and expected output
3. Quick command retrieval during active pentesting sessions
4. Easy addition of new commands through interactive interface
5. Modular structure for adding new tools effortlessly
6. Tool categorization for better organization
7. Copy-to-clipboard functionality (execution to be added later)

### Target Platform
- Linux (primary)
- CLI-only (no TUI for now)

---

## Architecture Design

### Architecture Pattern

```
AbstractTool (Base Class)
    ↓
Concrete Tool Classes (Nmap, SMB, Netcat, etc.)
    ↓
CommandManager (Orchestrator)
    ↓
CLI Interface (Interactive & Quick Mode)
```

### Design Principles

1. **Abstract Base Class Pattern**: Forces consistency across all tools while allowing flexibility
2. **YAML Storage**: Human-readable, version-control friendly, easy manual editing if needed
3. **Template-based Commands**: `{param}` placeholders for flexible generation
4. **Command Reference Format**: `tool:command_id` for unique identification
5. **Stub Execution Method**: Designed for future implementation without breaking changes
6. **Rich CLI Output**: Beautiful terminal output for better UX
7. **Clipboard Integration**: Seamless workflow during pentesting sessions
8. **Category System**: Logical organization of tools by purpose

---

## Project Structure

```
htb-automations/
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── base_tool.py           # Abstract base class for all tools
│   │   ├── command.py             # Command data model
│   │   ├── command_manager.py     # Central command orchestrator
│   │   ├── storage.py             # YAML storage handler
│   │   └── executor.py            # Command executor (stub for future)
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── nmap_tool.py           # Nmap implementation
│   │   ├── smb_tool.py            # SMB implementation
│   │   ├── netcat_tool.py         # Netcat implementation
│   │   └── ...                    # Future tools
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py                # CLI entry point
│   │   ├── commands/
│   │   │   ├── __init__.py
│   │   │   ├── add.py             # Interactive add command
│   │   │   ├── edit.py            # Edit existing command
│   │   │   ├── delete.py          # Delete command
│   │   │   ├── list.py            # List commands
│   │   │   ├── search.py          # Search commands
│   │   │   ├── show.py            # Show command details
│   │   │   ├── generate.py        # Generate command
│   │   │   └── tool.py            # Tool management
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── formatter.py       # Output formatting with Rich
│   │       ├── clipboard.py       # Clipboard operations
│   │       ├── prompts.py         # Interactive prompts with validation
│   │       └── validators.py      # Input validators
│   └── utils/
│       ├── __init__.py
│       └── helpers.py             # General utilities
├── data/
│   └── commands/                  # Command database (YAML)
│       ├── nmap.yaml
│       ├── smb.yaml
│       ├── netcat.yaml
│       └── ...
├── templates/
│   └── tool_template.yaml         # Template for new tools
├── tests/
│   ├── __init__.py
│   ├── test_base_tool.py
│   ├── test_command_manager.py
│   ├── test_storage.py
│   └── ...
├── .gitignore
├── requirements.txt
├── setup.py                       # Package installation
├── README.md
└── config.yaml                    # Global config (paths, defaults, categories)
```

---

## Core Classes & Interfaces

### 1. Abstract Base Class (base_tool.py)

```python
# src/core/base_tool.py
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from .command import Command

class BaseTool(ABC):
    """
    Abstract base class for all pentesting tools.
    Each tool must implement this interface for consistency.
    """
    
    def __init__(self, storage):
        self.storage = storage
        self._commands: List[Command] = []
        self.load_commands()
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name (e.g., 'nmap')"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description"""
        pass
    
    @property
    @abstractmethod
    def category(self) -> str:
        """
        Tool category for organization.
        Categories: reconnaissance, scanning, enumeration, 
                   exploitation, post-exploitation, cracking, 
                   web, wireless, misc
        """
        pass
    
    def load_commands(self) -> None:
        """Load commands from storage"""
        self._commands = self.storage.load_tool_commands(self.name)
    
    def save_commands(self) -> None:
        """Save commands to storage"""
        self.storage.save_tool_commands(self.name, self._commands)
    
    def add_command(self, command: Command) -> None:
        """Add a new command"""
        self._commands.append(command)
        self.save_commands()
    
    def update_command(self, command_id: str, updated_command: Command) -> bool:
        """Update an existing command"""
        for i, cmd in enumerate(self._commands):
            if cmd.id == command_id:
                self._commands[i] = updated_command
                self.save_commands()
                return True
        return False
    
    def delete_command(self, command_id: str) -> bool:
        """Delete a command"""
        original_len = len(self._commands)
        self._commands = [cmd for cmd in self._commands if cmd.id != command_id]
        if len(self._commands) < original_len:
            self.save_commands()
            return True
        return False
    
    def get_command(self, command_id: str) -> Optional[Command]:
        """Get command by ID"""
        return next((cmd for cmd in self._commands if cmd.id == command_id), None)
    
    def get_all_commands(self) -> List[Command]:
        """Get all commands for this tool"""
        return self._commands
    
    def search_commands(self, query: str = None, tags: List[str] = None) -> List[Command]:
        """Search commands by query or tags"""
        results = self._commands
        
        if query:
            query_lower = query.lower()
            results = [cmd for cmd in results if 
                      query_lower in cmd.name.lower() or 
                      query_lower in cmd.explanation.lower() or
                      query_lower in cmd.command.lower()]
        
        if tags:
            results = [cmd for cmd in results if any(tag in cmd.tags for tag in tags)]
        
        return results
    
    def generate_command(self, command_id: str, params: Dict[str, str]) -> str:
        """Generate command string with parameters"""
        command = self.get_command(command_id)
        if not command:
            raise ValueError(f"Command {command_id} not found")
        return command.render(params)
    
    # Future execution method (stub for now)
    def execute_command(self, command_id: str, params: Dict[str, str], 
                       dry_run: bool = True) -> Dict:
        """
        Execute command (to be implemented later).
        For now, returns the command string only.
        """
        cmd_string = self.generate_command(command_id, params)
        
        if dry_run:
            return {
                'command': cmd_string,
                'executed': False,
                'output': None
            }
        else:
            # Future implementation will execute here
            raise NotImplementedError("Execution not yet implemented")
```

### 2. Command Model (command.py)

```python
# src/core/command.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import re

@dataclass
class Parameter:
    """Command parameter definition"""
    name: str
    description: str
    required: bool = True
    default: Optional[str] = None

@dataclass
class Example:
    """Command example with expected output"""
    input: str
    output: str
    description: Optional[str] = None

@dataclass
class Command:
    """Command data model"""
    id: str
    name: str
    command: str  # Template with {param} placeholders
    explanation: str
    parameters: List[Parameter] = field(default_factory=list)
    examples: List[Example] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    
    def render(self, params: Dict[str, str]) -> str:
        """Render command template with provided parameters"""
        # Validate required parameters
        for param in self.parameters:
            if param.required and param.name not in params:
                if param.default:
                    params[param.name] = param.default
                else:
                    raise ValueError(f"Required parameter '{param.name}' not provided")
        
        # Substitute parameters
        rendered = self.command
        for key, value in params.items():
            rendered = rendered.replace(f"{{{key}}}", value)
        
        return rendered
    
    def get_parameter_placeholders(self) -> List[str]:
        """Extract parameter names from command template"""
        return re.findall(r'\{(\w+)\}', self.command)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for YAML serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'command': self.command,
            'explanation': self.explanation,
            'parameters': [
                {
                    'name': p.name,
                    'description': p.description,
                    'required': p.required,
                    'default': p.default
                } for p in self.parameters
            ],
            'examples': [
                {
                    'input': e.input,
                    'output': e.output,
                    'description': e.description
                } for e in self.examples
            ],
            'tags': self.tags,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Command':
        """Create Command from dictionary (YAML deserialization)"""
        parameters = [
            Parameter(**p) for p in data.get('parameters', [])
        ]
        examples = [
            Example(**e) for e in data.get('examples', [])
        ]
        
        return cls(
            id=data['id'],
            name=data['name'],
            command=data['command'],
            explanation=data['explanation'],
            parameters=parameters,
            examples=examples,
            tags=data.get('tags', []),
            notes=data.get('notes')
        )
```

### 3. Command Manager (command_manager.py)

```python
# src/core/command_manager.py
from typing import List, Dict, Optional, Type
from .base_tool import BaseTool
from .storage import Storage

class CommandManager:
    """
    Central orchestrator for all tools and commands.
    Manages tool registry and provides unified interface.
    """
    
    def __init__(self, storage: Storage):
        self.storage = storage
        self._tools: Dict[str, BaseTool] = {}
    
    def register_tool(self, tool_class: Type[BaseTool]) -> None:
        """Register a tool class"""
        tool = tool_class(self.storage)
        self._tools[tool.name] = tool
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get tool by name"""
        return self._tools.get(tool_name)
    
    def list_tools(self, category: str = None) -> List[Dict]:
        """List all registered tools, optionally filtered by category"""
        tools = [
            {
                'name': tool.name,
                'description': tool.description,
                'category': tool.category,
                'command_count': len(tool.get_all_commands())
            }
            for tool in self._tools.values()
        ]
        
        if category:
            tools = [t for t in tools if t['category'] == category]
        
        return sorted(tools, key=lambda x: (x['category'], x['name']))
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        categories = set(tool.category for tool in self._tools.values())
        return sorted(categories)
    
    def search_all(self, query: str = None, tags: List[str] = None, 
                   category: str = None) -> Dict[str, List]:
        """Search across all tools"""
        results = {}
        for tool_name, tool in self._tools.items():
            # Filter by category if specified
            if category and tool.category != category:
                continue
            
            commands = tool.search_commands(query, tags)
            if commands:
                results[tool_name] = commands
        return results
    
    def get_command(self, command_ref: str):
        """
        Get command by reference (format: 'tool:command_id')
        e.g., 'nmap:basic-scan'
        """
        if ':' not in command_ref:
            raise ValueError("Command reference must be in format 'tool:command_id'")
        
        tool_name, command_id = command_ref.split(':', 1)
        tool = self.get_tool(tool_name)
        
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        return tool.get_command(command_id)
    
    def generate_command(self, command_ref: str, params: Dict[str, str]) -> str:
        """Generate command from reference"""
        tool_name, command_id = command_ref.split(':', 1)
        tool = self.get_tool(tool_name)
        return tool.generate_command(command_id, params)
```

### 4. Storage Handler (storage.py)

```python
# src/core/storage.py
import yaml
from pathlib import Path
from typing import List
from .command import Command

class Storage:
    """Handles YAML storage operations"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def get_tool_file_path(self, tool_name: str) -> Path:
        """Get YAML file path for a tool"""
        return self.data_dir / f"{tool_name}.yaml"
    
    def load_tool_commands(self, tool_name: str) -> List[Command]:
        """Load commands from YAML file"""
        file_path = self.get_tool_file_path(tool_name)
        
        if not file_path.exists():
            return []
        
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        if not data or 'commands' not in data:
            return []
        
        return [Command.from_dict(cmd) for cmd in data['commands']]
    
    def save_tool_commands(self, tool_name: str, commands: List[Command]) -> None:
        """Save commands to YAML file"""
        file_path = self.get_tool_file_path(tool_name)
        
        data = {
            'tool': tool_name,
            'commands': [cmd.to_dict() for cmd in commands]
        }
        
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    def tool_exists(self, tool_name: str) -> bool:
        """Check if tool YAML file exists"""
        return self.get_tool_file_path(tool_name).exists()
    
    def create_tool_file(self, tool_name: str, description: str = "") -> None:
        """Create empty YAML file for new tool"""
        file_path = self.get_tool_file_path(tool_name)
        
        data = {
            'tool': tool_name,
            'description': description,
            'commands': []
        }
        
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
```

### 5. Interactive Prompts (prompts.py)

```python
# src/cli/utils/prompts.py
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from typing import List, Optional, Dict
from src.core.command import Parameter

console = Console()

class InteractivePrompts:
    """User-friendly interactive prompts with Rich formatting"""
    
    @staticmethod
    def select_tool(tools: List[Dict]) -> str:
        """Interactive tool selection with category grouping"""
        # Group tools by category
        by_category = {}
        for tool in tools:
            cat = tool['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(tool)
        
        # Display grouped list
        console.print("\n[bold cyan]Available Tools:[/bold cyan]")
        for category, cat_tools in sorted(by_category.items()):
            console.print(f"\n[yellow]{category}[/yellow]")
            for tool in cat_tools:
                console.print(f"  • {tool['name']:<15} - {tool['description']}")
        
        # Prompt for selection
        tool_name = Prompt.ask("\n[bold]Select tool[/bold]")
        return tool_name
    
    @staticmethod
    def input_command_details() -> Dict:
        """Prompt for basic command details"""
        console.print("\n[bold cyan]Command Details[/bold cyan]")
        
        name = Prompt.ask("Command Name")
        
        # Auto-generate ID from name
        suggested_id = name.lower().replace(' ', '-').replace('_', '-')
        command_id = Prompt.ask("Command ID", default=suggested_id)
        
        command = Prompt.ask("Command Template (use {param} for variables)")
        explanation = Prompt.ask("Explanation")
        
        return {
            'id': command_id,
            'name': name,
            'command': command,
            'explanation': explanation
        }
    
    @staticmethod
    def configure_parameter(param_name: str) -> Parameter:
        """Interactive parameter configuration"""
        console.print(f"\n[bold cyan]Configure Parameter: {param_name}[/bold cyan]")
        
        description = Prompt.ask("  Description")
        required = Confirm.ask("  Required?", default=True)
        default = None
        
        if not required:
            default = Prompt.ask("  Default value (optional)", default="")
            default = default if default else None
        
        return Parameter(
            name=param_name,
            description=description,
            required=required,
            default=default
        )
    
    @staticmethod
    def input_tags(suggestions: List[str] = None) -> List[str]:
        """Prompt for tags with suggestions"""
        console.print("\n[bold cyan]Tags[/bold cyan]")
        
        if suggestions:
            console.print(f"  Suggestions: {', '.join(suggestions)}")
        
        tags_input = Prompt.ask("Tags (comma-separated)")
        tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
        
        return tags
    
    @staticmethod
    def add_example() -> Optional[Dict]:
        """Prompt to add an example"""
        if not Confirm.ask("\n[bold]Add an example?[/bold]", default=False):
            return None
        
        console.print("\n[bold cyan]Command Example[/bold cyan]")
        
        example_input = Prompt.ask("  Example Input")
        
        console.print("  Example Output (paste, then press Enter twice):")
        output_lines = []
        while True:
            line = input("  ")
            if line == "" and output_lines and output_lines[-1] == "":
                break
            output_lines.append(line)
        
        output = "\n".join(output_lines[:-1])  # Remove last empty line
        
        description = Prompt.ask("  Example Description (optional)", default="")
        
        return {
            'input': example_input,
            'output': output,
            'description': description if description else None
        }
    
    @staticmethod
    def review_and_confirm(command_data: Dict) -> bool:
        """Display command summary and ask for confirmation"""
        console.print("\n[bold cyan]Review Command[/bold cyan]")
        
        panel_content = f"""
[yellow]Tool:[/yellow] {command_data.get('tool', 'N/A')}
[yellow]ID:[/yellow] {command_data['id']}
[yellow]Name:[/yellow] {command_data['name']}
[yellow]Command:[/yellow] {command_data['command']}
[yellow]Explanation:[/yellow] {command_data['explanation']}
[yellow]Parameters:[/yellow] {len(command_data.get('parameters', []))}
[yellow]Examples:[/yellow] {len(command_data.get('examples', []))}
[yellow]Tags:[/yellow] {', '.join(command_data.get('tags', []))}
"""
        
        console.print(Panel(panel_content, title="Command Summary"))
        
        return Confirm.ask("\n[bold]Save this command?[/bold]", default=True)
```

---

## Interactive CLI Interface

### Command Structure

```bash
htb <command> [options]

Commands:
  add       Add a new command (interactive, user-friendly)
  edit      Edit an existing command (interactive)
  delete    Delete a command
  list      List commands
  search    Search commands
  show      Show command details
  gen       Generate command with parameters (copies to clipboard)
  tool      Manage tools
  
Options:
  --help    Show help
  --version Show version
```

### Interactive Add Command Flow

The `htb add` command will be **highly interactive** with step-by-step prompts:

```bash
$ htb add

# Step 1: Select Tool
┌─────────────────────────────────────────────────┐
│  Select Tool                                     │
├─────────────────────────────────────────────────┤
│  [reconnaissance]                                │
│    → nmap    - Network exploration tool          │
│      netcat  - Network debugging tool            │
│                                                  │
│  [enumeration]                                   │
│      smb     - SMB enumeration tool              │
│      enum4linux - Windows/Samba enumeration      │
│                                                  │
│  [+] Add new tool                                │
└─────────────────────────────────────────────────┘
Select tool (or type name): nmap

# Step 2: Command ID (auto-suggested based on name)
Command ID: [auto-generated from name, editable]

# Step 3: Command Name
Command Name: Service Version Detection

# Step 4: Command Template
Command Template (use {param} for variables): nmap -sV {target} {ports}
Detected parameters: target, ports

# Step 5: Explanation
Explanation: Probes open ports to determine service/version info

# Step 6: Configure Parameters (interactive for each detected param)
┌─────────────────────────────────────────────────┐
│  Configure Parameter: target                     │
├─────────────────────────────────────────────────┤
│  Description: Target IP address or hostname      │
│  Required? (Y/n): Y                              │
│  Default value (optional):                       │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  Configure Parameter: ports                      │
├─────────────────────────────────────────────────┤
│  Description: Port specification (e.g., -p 80)   │
│  Required? (Y/n): n                              │
│  Default value (optional):                       │
└─────────────────────────────────────────────────┘

# Step 7: Tags (with suggestions)
Tags (comma-separated): enumeration, version, service-detection
Suggested tags: scanning, enumeration, reconnaissance, exploitation, ...

# Step 8: Add Example? (optional, can add multiple)
Add an example? (y/N): y

Example Input: nmap -sV 192.168.1.1
Example Output (paste, then Ctrl+D to finish):
22/tcp  open  ssh     OpenSSH 7.6p1 Ubuntu
80/tcp  open  http    Apache httpd 2.4.29
^D
Example Description (optional): Basic version scan output

Add another example? (y/N): n

# Step 9: Notes (optional)
Additional notes (optional): Useful for identifying vulnerable versions

# Step 10: Confirmation
┌─────────────────────────────────────────────────┐
│  Review Command                                  │
├─────────────────────────────────────────────────┤
│  Tool: nmap                                      │
│  ID: service-version                             │
│  Name: Service Version Detection                │
│  Command: nmap -sV {target} {ports}              │
│  Explanation: Probes open ports to...            │
│  Parameters: 2 (target*, ports)                  │
│  Examples: 1                                     │
│  Tags: enumeration, version, service-detection   │
└─────────────────────────────────────────────────┘

Save this command? (Y/n): Y
✓ Command 'nmap:service-version' saved successfully!
```

### Full CLI Command Reference

```bash
# === TOOL MANAGEMENT ===

# List all tools
htb tool list

# List tools by category
htb tool list --category reconnaissance

# List all categories
htb tool categories

# Add new tool (interactive)
htb tool add

# Add new tool (quick)
htb tool add gobuster --description "Directory bruster" --category web


# === ADD COMMANDS ===

# Add command (fully interactive - RECOMMENDED)
htb add

# Add to specific tool (semi-interactive)
htb add nmap

# Quick add (all flags)
htb add nmap \
  --id aggressive-scan \
  --name "Aggressive Scan" \
  --cmd "nmap -A {target}" \
  --explain "OS detection, version detection, script scanning, traceroute" \
  --param target:"Target IP":required \
  --tag scanning,aggressive,os-detection


# === EDIT COMMANDS ===

# Edit command (interactive)
htb edit nmap:basic-scan

# Quick edit (update specific field)
htb edit nmap:basic-scan --explanation "New explanation"


# === DELETE COMMANDS ===

# Delete command (with confirmation)
htb delete nmap:basic-scan

# Force delete (no confirmation)
htb delete nmap:basic-scan --force


# === LIST COMMANDS ===

# List all commands (all tools)
htb list

# List commands for specific tool
htb list nmap

# List by category
htb list --category scanning

# List with details (show parameters)
htb list nmap --detailed


# === SEARCH COMMANDS ===

# Search by keyword
htb search "version detection"

# Search by tag
htb search --tag enumeration

# Search by multiple tags
htb search --tag scanning,aggressive

# Search in specific tool
htb search --tool nmap --tag scanning

# Search by category
htb search --category reconnaissance


# === SHOW COMMANDS ===

# Show full command details
htb show nmap:basic-scan

# Show with syntax highlighting
htb show nmap:basic-scan --highlight


# === GENERATE COMMANDS ===

# Generate and copy to clipboard (interactive prompt for params)
htb gen nmap:basic-scan

# Generate with parameters
htb gen nmap:basic-scan --target 10.10.10.5

# Generate without copying
htb gen nmap:basic-scan --target 10.10.10.5 --no-copy

# Generate and display command only (no copy)
htb gen nmap:basic-scan --target 10.10.10.5 --print-only

# Interactive parameter input
htb gen nmap:service-version
# Will prompt:
# → target: 10.10.10.5
# → ports (optional, press Enter to skip): -p 80,443
# Generated: nmap -sV 10.10.10.5 -p 80,443
# ✓ Copied to clipboard!

# Store generated command as full command (after generation)
htb gen nmap:version-script-scan -p target=10.10.10.5 -p ports=80,443
# Generated: nmap -sV -sC -p 80,443 10.10.10.5
# Store as full command? [y/N]: y
# Command ID: my-custom-scan
# Saved as nmap:my-custom-scan
```

---

## Command Chaining (Sub-command Composition)

Tools like nmap support many options (-sV, -sC, -p, --script). Commands can be built from **sub-commands** (composable flags):

- **Sub-commands:** Reusable flags defined per tool (e.g. `-sV`, `-sC`, `-p {ports}`)
- **Composition:** A command selects which sub-commands to include
- **Store as full command:** After generating, user can save the result as a new command in the tool's list

**Flow:**
1. User has a command with sub-commands (e.g. version-script-scan with sV, sC, ports)
2. `htb gen nmap:version-script-scan` prompts for params, generates full command
3. After output: "Store as full command? [y/N]" – if yes, prompt for id/name and save
4. Saved command is a regular full template (stored in commands list for reuse)

See [docs/COMMAND_CHAINING_PLAN.md](docs/COMMAND_CHAINING_PLAN.md) for full implementation plan.

---

## Data Format

### YAML Structure

```yaml
# data/commands/nmap.yaml
tool: nmap
description: "Network exploration and security auditing"
category: scanning
commands:
  - id: basic-scan
    name: "Basic Port Scan"
    command: "nmap {target}"
    explanation: "Performs default TCP scan on top 1000 ports"
    parameters:
      - name: target
        description: "Target IP address or hostname"
        required: true
        default: null
    examples:
      - input: "nmap 192.168.1.1"
        output: |
          Starting Nmap 7.94
          PORT    STATE SERVICE
          22/tcp  open  ssh
          80/tcp  open  http
          443/tcp open  https
        description: "Basic scan output showing open ports"
    tags: [basic, scanning, tcp, reconnaissance]
    notes: "Default scan without root privileges"
    
  - id: service-version
    name: "Service Version Detection"
    command: "nmap -sV {target} {ports}"
    explanation: "Probes open ports to determine service versions"
    parameters:
      - name: target
        description: "Target IP address or hostname"
        required: true
      - name: ports
        description: "Port specification (e.g., -p 80,443 or -p-)"
        required: false
        default: ""
    examples:
      - input: "nmap -sV 192.168.1.1"
        output: |
          22/tcp  open  ssh     OpenSSH 7.6p1 Ubuntu
          80/tcp  open  http    Apache httpd 2.4.29
          443/tcp open  ssl/http Apache httpd 2.4.29
    tags: [enumeration, version, service-detection]
    notes: "Useful for identifying vulnerable service versions"
```

---

## Configuration

### config.yaml

```yaml
# config.yaml
data_dir: "data/commands"

# Tool categories
categories:
  - reconnaissance
  - scanning
  - enumeration
  - exploitation
  - post-exploitation
  - cracking
  - web
  - wireless
  - misc

# Common tag suggestions
tag_suggestions:
  - basic
  - advanced
  - aggressive
  - stealth
  - fast
  - comprehensive
  - tcp
  - udp
  - version
  - os-detection
  - script
  - authentication
  - brute-force
  - file-transfer

# CLI settings
clipboard_enabled: true
syntax_highlighting: true
confirm_delete: true
```

---

## Dependencies

### requirements.txt

```
click>=8.0.0          # CLI framework
PyYAML>=6.0           # YAML parsing
rich>=13.0.0          # Terminal formatting & interactive prompts
pyperclip>=1.8.2      # Clipboard operations
```

---

## Implementation Plan

### Phase 1: Core Foundation (Days 1-2)
- [x] Project structure setup
- [x] `Command` data model with full serialization
- [x] `BaseTool` abstract class with category support
- [x] `Storage` handler with YAML I/O
- [x] `CommandManager` with category filtering
- [x] Configuration file loader
- [x] Basic tests for core models

### Phase 2: Tool Registry & Concrete Tools (Day 3)
- [x] Implement 3 concrete tools with categories:
  - NmapTool (scanning)
  - SMBTool (enumeration)
  - NetcatTool (misc)
- [x] Create initial command database (3-5 commands per tool)
- [x] Tool registration in CLI

### Phase 3: Interactive CLI - Add Command (Days 4-5)
- [x] `InteractivePrompts` utility class with Rich
- [x] `htb add` - fully interactive flow:
  - Tool selection with category display
  - Command details input
  - Parameter auto-detection and configuration
  - Tag input with suggestions
  - Example input (multi-line support)
  - Review and confirmation
- [x] Input validation at each step
- [x] Beautiful Rich-formatted output

### Phase 4: CLI - List, Show, Search (Day 6)
- [x] `htb list` with category filtering and detailed view
- [x] `htb show` with syntax highlighting
- [x] `htb search` with multi-criteria filtering
- [x] Rich tables and panels for all outputs

### Phase 5: CLI - Generate & Tool Management (Day 7)
- [x] `htb gen` with interactive parameter prompts
- [x] Clipboard integration
- [x] `htb tool list` with category grouping
- [x] `htb tool add` for creating new tools
- [x] `htb edit` for updating existing commands
- [x] `htb delete` with confirmation

### Phase 6: Polish & Documentation (Day 8)
- [x] Error handling with helpful messages
- [x] `--help` text for all commands
- [x] README with screenshots/examples
- [x] setup.py for installation (`pip install -e .`)
- [x] Example workflow documentation

---

## Key Features

### User-Friendly Interactive Interface ✨
1. **Step-by-step prompts** with clear instructions
2. **Auto-detection** of parameters from command templates
3. **Smart defaults** (auto-generated IDs, suggested tags)
4. **Multi-line input** for examples and outputs
5. **Review before save** with formatted summary
6. **Rich terminal UI** with colors, panels, and tables
7. **Category-based organization** for easy navigation

### Modular & Extensible 🔧
1. **Abstract base class** enforces consistency
2. **Simple tool creation** (3-line implementation)
3. **YAML storage** for easy manual editing if needed
4. **Category system** for logical grouping
5. **Tag system** for flexible filtering

### Workflow Optimized ⚡
1. **Fast command generation** with clipboard copy
2. **Flexible search** (by tool, tag, category, keyword)
3. **Edit and delete** capabilities
4. **Future-ready** for command execution
5. **No database setup** required

---

## Example Implementations

### Example Concrete Tool

```python
# src/tools/nmap_tool.py
from src.core.base_tool import BaseTool

class NmapTool(BaseTool):
    @property
    def name(self) -> str:
        return "nmap"
    
    @property
    def description(self) -> str:
        return "Network exploration and security auditing"
    
    @property
    def category(self) -> str:
        return "scanning"
```

### Example Tool Registration

```python
# In CLI main.py
from src.core.command_manager import CommandManager
from src.core.storage import Storage
from src.tools.nmap_tool import NmapTool
from src.tools.smb_tool import SMBTool
from src.tools.netcat_tool import NetcatTool

# Initialize
storage = Storage("data/commands")
manager = CommandManager(storage)

# Register tools
manager.register_tool(NmapTool)
manager.register_tool(SMBTool)
manager.register_tool(NetcatTool)
```

---

## Future Extensibility

### Command Execution (Future Phase)
The `execute_command()` method in `BaseTool` is already stubbed for future implementation:

```python
# Future implementation will:
1. Use subprocess.run() for safe execution
2. Capture output in real-time
3. Add confirmation prompts
4. Support dry-run mode
5. Log execution history
```

### Additional Features (Future Roadmap)
- Command history tracking
- Export/import command sets
- Integration with note-taking tools (Obsidian, Notion)
- Web UI using Flask/FastAPI
- Command chaining with sub-commands (see Command Chaining section above)
- Variable templates (save commonly used IPs)
- HTB API integration for machine notes
- Bash/Zsh completion scripts

---

## Validation Checklist

- ✅ User-friendly interactive interface for adding commands
- ✅ YAML accessible through CLI (no manual editing required)
- ✅ Tool categorization system
- ✅ Abstract base class with all necessary methods
- ✅ Modular structure for easy tool addition
- ✅ Clipboard integration for workflow
- ✅ Edit and delete capabilities
- ✅ Rich terminal UI with colors and formatting
- ✅ Future-ready for command execution
- ✅ Comprehensive CLI command reference
- ✅ Clear implementation roadmap

---

**Status:** ✅ Specification Approved - Ready for Implementation  
**Next Step:** Begin Phase 1 - Core Foundation

