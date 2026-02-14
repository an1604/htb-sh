# Flows Feature - Technical Specification

**Version:** 1.0  
**Date:** February 14, 2026  
**Status:** Draft - Ready for Review

---

## Table of Contents

1. [Overview](#overview)
2. [Core Principle](#core-principle)
3. [Store and Load Flows](#store-and-load-flows)
4. [Show Flow on Command Line](#show-flow-on-command-line)
5. [Data Models](#data-models)
6. [Storage Structure](#storage-structure)
7. [Script Generation](#script-generation)
8. [CLI Commands](#cli-commands)
9. [Implementation Phases](#implementation-phases)
10. [File Structure](#file-structure)
11. [Backward Compatibility](#backward-compatibility)

---

## Overview

**Flows** are sequences of multiple commands that form a complete workflow (e.g., SMB enumeration: list shares → connect to share → scan ports). Users can:

1. **Store** flows as YAML definitions
2. **Load** a flow when the user requests it by flow ID
3. **Show** flow details on the command line (list and detailed view)
4. **Generate** executable scripts (bash or Python) from flows — **without executing them**

Flows build on top of existing commands; each step references a command by `tool:command_id`.

---

## Core Principle

**Flows generate executable scripts but do NOT execute them.**

- The tool only produces script content (display, clipboard, or save to file).
- The user reviews and runs the generated script manually.
- No direct execution of flows from within the tool in this phase.

---

## Store and Load Flows

### Storage

- **Location:** `data/flows/` (one YAML file per flow or one file containing multiple flows — implementation choice).
- **Format:** YAML with flow metadata, parameters, and steps (see [Storage Structure](#storage-structure)).
- **API:** Storage layer provides `load_flows()`, `save_flow(flow)`, and path helpers for flow files.

### Loading

- **When:** Load flows on demand when the user requests a specific flow (e.g., `htb flow show <flow_id>`, `htb flow gen <flow_id>`).
- **Lazy load:** Load all flow definitions once when the flow subsystem is first used (e.g., first `htb flow` subcommand), then serve from memory; or load a single flow by ID from disk when requested. Spec allows either; implementation should document the choice.
- **FlowManager** responsibilities:
  - `get_flow(flow_id: str) -> Optional[Flow]` — return flow by ID (load from storage if needed).
  - `list_flows(tag: Optional[str] = None) -> List[Flow]` — list flows, optionally filtered by tag.
  - `add_flow(flow: Flow)`, `update_flow(flow_id, flow)`, `delete_flow(flow_id)` for CRUD.

### Requirements Captured

- Flows are **stored** in the project (YAML under `data/flows/`).
- Flows are **loaded** when the user requests a specific flow (e.g., by flow ID in `show`, `gen`, `edit`, `delete`).

---

## Show Flow on Command Line

Two main ways to show flows: **list** (all or filtered) and **show** (single flow details).

### List Flows: `htb flow list`

**Command:** `htb flow list [--tag TAG] [--compact]`

**Full view (default):** Group by first tag (or "uncategorized"). For each flow show name, short description, step count, and tags.

**Example output:**

```
Available Flows (2 total)

[enumeration]
  • smb-enumeration        - Complete SMB enumeration workflow
    Steps: 3 | Tags: enumeration, smb, reconnaissance

[reconnaissance]
  • web-recon              - Full web application reconnaissance
    Steps: 5 | Tags: web, reconnaissance, fuzzing

---
Use 'htb flow show <flow-id>' for detailed view
```

**With `--tag enumeration`:** Only list flows that have that tag.

**With `--compact`:** Minimal one-line per flow, e.g.:

```
• smb-enumeration        - Complete SMB enumeration workflow
• web-recon             - Full web application reconnaissance
```

### Show Single Flow: `htb flow show <flow_id>`

**Command:** `htb flow show <flow_id> [--compact] [--json]`

**Full view (default):** Rich formatted output with:

- Header panel: flow name, ID, description, default format, tags
- Parameters section: name, required/optional, description, default
- Steps section: order, step id, command ref, description, parameter mappings, notes
- Flow-level notes
- Short usage examples (gen, preview, save)

**Example output:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Flow: SMB Full Enumeration                      │
├─────────────────────────────────────────────────────────────────────┤
│ ID:          smb-enumeration                                        │
│ Description: Complete SMB enumeration workflow: list shares,         │
│              connect to users share, scan ports                     │
│ Format:      bash                                                   │
│ Tags:        enumeration, smb, reconnaissance                       │
└─────────────────────────────────────────────────────────────────────┘

[Parameters]
  • target (required)    - Target IP address
  • username (optional)  - Username for authentication [default: guest]

[Steps] (3 total)

  1. list-shares
     Command: smbclient:lists-the-available-smb-shares
     Description: List all available SMB shares
     Parameters:
       host = {target}
     Note: Run this first to discover available shares

  2. connect-users-share
     Command: smbclient:connects-to-the-users-smb-share
     Description: Connect to the users share
     Parameters:
       host = {target}
     Note: May require credentials if not accessible anonymously

  3. scan-ports
     Command: nmap:basic-scan
     Description: Scan target for open ports
     Parameters:
       target = {target}

[Notes]
Run this flow after discovering SMB service (port 445) on target

[Usage]
Generate script: htb flow gen smb-enumeration --target <IP>
Preview:         htb flow gen smb-enumeration --target <IP> --preview
Save to file:    htb flow gen smb-enumeration --target <IP> --save script.sh
```

**With `--compact`:** Brief text summary (name, id, parameters, step count, command refs per step, tags).

**With `--json`:** Output flow as JSON (e.g. for scripting); structure should match the in-memory flow representation.

### Requirements Captured

- Flows are **shown on the command line** via `htb flow list` and `htb flow show <flow_id>` with the behavior and formats described above.

---

## Data Models

### FlowStep

A single step in a flow. No execution semantics (e.g. capture_output) in this spec.

```python
@dataclass
class FlowStep:
    id: str                           # Unique within flow (e.g. "list-shares")
    command_ref: str                  # Format: "tool:command_id"
    parameters: Dict[str, str]         # Param values; may use flow params as {param}
    description: Optional[str] = None
    notes: Optional[str] = None
```

### Flow

```python
@dataclass
class Flow:
    id: str
    name: str
    description: str
    steps: List[FlowStep]
    flow_parameters: List[Parameter] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None

    # Script generation settings
    default_format: str = "bash"       # "bash" | "python"
    add_error_handling: bool = True
    add_comments: bool = True
```

Serialization: `to_dict()` and `from_dict()` (or equivalent) for YAML read/write.

---

## Storage Structure

### YAML Example

```yaml
# data/flows/smb-enumeration.yaml
flow: smb-enumeration
id: smb-enumeration
name: "SMB Full Enumeration"
description: "Complete SMB enumeration workflow: list shares, connect to users share, scan ports"

flow_parameters:
  - name: target
    description: "Target IP address"
    required: true
  - name: username
    description: "Username for authentication"
    required: false
    default: "guest"

steps:
  - id: list-shares
    command_ref: "smbclient:lists-the-available-smb-shares"
    description: "List all available SMB shares"
    parameters:
      host: "{target}"
    notes: "Run this first to discover available shares"

  - id: connect-users-share
    command_ref: "smbclient:connects-to-the-users-smb-share"
    description: "Connect to the users share"
    parameters:
      host: "{target}"
    notes: "May require credentials if not accessible anonymously"

  - id: scan-ports
    command_ref: "nmap:basic-scan"
    description: "Scan target for open ports"
    parameters:
      target: "{target}"

tags: [enumeration, smb, reconnaissance]
default_format: bash
add_error_handling: true
add_comments: true
notes: "Run this flow after discovering SMB service (port 445) on target"
```

---

## Script Generation

Flows are turned into scripts by a **FlowScriptGenerator** (no execution). The tool only generates script text.

### FlowScriptGenerator

- **Location:** e.g. `src/core/flow_script_generator.py`
- **Inputs:** A `Flow`, flow parameter values `Dict[str, str]`, and output format (`bash` or `python`).
- **Outputs:** Script as string; optionally write to file and set executable bit.

**Methods:**

- `generate_script(flow, flow_params, format="bash") -> str` — full script with shebang, comments, and step commands.
- `preview_commands(flow, flow_params) -> List[str]` — ordered list of command strings only (no script wrapper).
- `save_script(script, filepath, make_executable=True)` — write script to file; on Unix set executable bit when `make_executable` is True.

Parameter substitution: step `parameters` and flow-level `flow_parameters` are resolved so that placeholders like `{target}` in step parameters are replaced by the provided flow parameter values when generating the script or preview.

### Generated Script Characteristics

- **Bash:** Shebang, optional `set -e`, flow metadata as comments, variables for flow parameters, echoed step descriptions, then the actual commands.
- **Python:** Shebang, docstring with flow metadata, variables for flow parameters, function or inline runs with subprocess (or equivalent), step descriptions and commands.

No execution of these scripts is performed by the tool.

---

## CLI Commands

### Flow Subcommand Group

All flow operations under: `htb flow <subcommand> [options]`.

### Subcommands and Flags

| Command | Purpose |
|--------|---------|
| `htb flow list [--tag TAG] [--compact]` | List flows; optional tag filter and compact output |
| `htb flow show <flow_id> [--compact] [--json]` | Show flow details (see [Show Flow on Command Line](#show-flow-on-command-line)) |
| `htb flow add` | Interactive flow creation (steps, parameters, tags) |
| `htb flow gen <flow_id> [options]` | Generate script from flow (see below) |
| `htb flow edit <flow_id>` | Edit existing flow |
| `htb flow delete <flow_id>` | Delete a flow |
| `htb flow search [query] [--tag TAG]` | Search flows by query and/or tag |

### `htb flow gen` Flags

| Flag | Type | Description |
|------|------|-------------|
| `--save FILE` | str | Save script to file instead of only displaying |
| `--format bash\|python` | str | Output format (default: flow’s `default_format` or bash) |
| `--preview` | bool | Output only the list of commands (no script wrapper) |
| `--no-copy` | bool | Do not copy to clipboard; only display (or save) |
| `--param NAME=VALUE` | str | Pass flow parameter (repeatable) |
| `--executable` | bool | When saving, make file executable (default: true on save) |

**Examples:**

```bash
# Generate and display (and copy to clipboard unless --no-copy)
htb flow gen smb-enumeration --param target=10.10.10.5

# Save to file
htb flow gen smb-enumeration --param target=10.10.10.5 --save enum.sh

# Python format and save
htb flow gen smb-enumeration --param target=10.10.10.5 --format python --save enum.py

# Preview commands only
htb flow gen smb-enumeration --param target=10.10.10.5 --preview

# Display only, no clipboard
htb flow gen smb-enumeration --param target=10.10.10.5 --no-copy
```

---

## Implementation Phases

### Phase 1: Core flow models and storage

- Add `FlowStep` and `Flow` dataclasses with serialization (`to_dict` / `from_dict`).
- Add flow storage methods (load/save, paths under `data/flows/`).
- Ensure flows can be stored and loaded by ID.

### Phase 2: FlowManager and script generation

- Implement `FlowManager` (get_flow, list_flows, add_flow, update_flow, delete_flow).
- Implement `FlowScriptGenerator` (generate_script, preview_commands, save_script).
- Support bash and Python output formats and parameter substitution.

### Phase 3: CLI – list and show

- Implement `htb flow list` with optional `--tag` and `--compact`.
- Implement `htb flow show <flow_id>` with full, compact, and `--json` output as specified.

### Phase 4: CLI – gen, add, edit, delete, search

- Implement `htb flow gen` with all flags (--save, --format, --preview, --no-copy, --param, --executable).
- Implement `htb flow add` (interactive), `htb flow edit`, `htb flow delete`, `htb flow search`.

### Phase 5: Examples and documentation

- Add example flow YAMLs under `data/flows/`.
- Document flows in main SPEC or README and reference this spec.

---

## File Structure

Suggested additions/changes:

```
htb-automations/
├── data/
│   └── flows/                   # Flow definitions (YAML)
│       ├── smb-enumeration.yaml
│       └── ...
├── src/
│   ├── core/
│   │   ├── flow.py              # Flow, FlowStep models
│   │   ├── flow_manager.py      # Load, list, CRUD
│   │   └── flow_script_generator.py  # Script generation only
│   └── cli/
│       ├── commands/
│       │   └── flow.py          # htb flow * commands
│       └── utils/
│           └── flow_prompts.py  # Interactive prompts for add/edit
└── specs/
    └── FLOWS_SPEC.md            # This document
```

---

## Backward Compatibility

- Flows are additive: no change to existing command or tool behavior.
- Existing CLI commands (`htb add`, `htb gen`, `htb list`, etc.) remain unchanged.
- Flow data lives under `data/flows/`; command data remains under `data/commands/`.

---

## Summary

- **Store:** Flows are stored as YAML in `data/flows/` and managed by storage + FlowManager.
- **Load:** A flow is loaded when the user requests it (e.g. by flow ID in show/gen/edit/delete).
- **Show:** Flows are shown on the command line via `htb flow list` and `htb flow show <flow_id>` with full, compact, and optional JSON output.
- **Generate only:** The tool generates bash or Python scripts from flows and does not execute them; execution is left to the user.
