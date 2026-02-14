# Command Chaining - Implementation Plan

## Overview

Support building full commands from composable **command options** (flags). For tools like nmap with many options (-sV, -sC, -p, --script), users can add or remove options per command and build a full command from the composition.

**Terminology:** We use "composed" (not "chained") to avoid confusion with shell pipelines. Options like `-sV` are **CommandOption** instances (alternative name: SubCommand for backward compat in YAML).

**Example:** A user creates a command that combines `-sV` + `-sC` + `-p {ports}` + `--script {script}` → `nmap -sV -sC -p {ports} --script {script} {target}`

---

## Current State (from SPEC & codebase)

| Component | Current | Notes |
|-----------|---------|-------|
| **Command** | Single `command` string with `{param}` placeholders | e.g. `nmap -sV {target}` |
| **Parameters** | List of Parameter (name, description, required, default) | Inferred from template or explicit |
| **Storage** | YAML: `command`, `parameters`, `examples`, `tags` | One flat template per command |
| **Generation** | Substitute params into template | `render(params)` |
| **Add flow** | User enters full template or uses quick flags | No composability |

**Limitation:** Each command is a single template. To support multiple flag combinations (e.g. with/without -sC), users must create separate commands. No reuse of flag definitions.

---

## Proposed Design

### 1. Architecture Overview

```
ToolContext (tool name, options registry, base default)
    ↓
CommandTemplateBuilder (builds template from base + option ids)
    ↓
Command (data model with source: FlatTemplate | ComposedTemplate)
    ↓
1. get_template(builder) → resolve to final template string
2. render(params) → substitute {param} placeholders
```

### 2. CommandOption (model)

A reusable building block. Uses `Parameter` for param metadata (DRY):

```python
@dataclass
class CommandOption:  # alias: SubCommand in YAML for readability
    id: str
    flag: str
    description: str
    parameter: Optional[Parameter] = None  # None = flag-only (e.g. -sV)
```

**YAML (with parameter):**
```yaml
id: ports
flag: "-p"
description: "Port specification"
parameter:
  name: ports
  description: "Port spec (e.g., 80,443 or -)"
  required: false
  default: ""
```

**YAML (flag-only):**
```yaml
id: sV
flag: "-sV"
description: "Version detection"
# parameter: null or omitted
```

### 3. CommandSource (Flat vs Composed)

Explicit branching instead of scattered `if sub_command_ids`:

```python
@dataclass
class FlatTemplate:
    """Existing: single template string."""
    template: str

@dataclass
class ComposedTemplate:
    """New: base + option ids, resolved via CommandTemplateBuilder."""
    base_command: str
    option_ids: List[str]

# Command.source: Union[FlatTemplate, ComposedTemplate]
# Backward compat: Command with only `command` field → FlatTemplate(command)
```

=### 4. CommandTemplateBuilder

Extract build logic from Command. Single responsibility.

```python
# src/core/command_builder.py
class CommandTemplateBuilder:
    """Builds command template from base + options. Testable in isolation."""

    def __init__(self, options: Dict[str, CommandOption]):
        self._options = options

    def build(self, base_command: str, option_ids: List[str]) -> str:
        """Build full template. Returns string with {param} placeholders."""
        parts = [base_command]
        for opt_id in option_ids:
            opt = self._options.get(opt_id)
            if opt:
                parts.append(opt.flag)
                if opt.parameter:
                    parts.append("{" + opt.parameter.name + "}")
        return " ".join(parts)

    def get_parameters(self, base_command: str, option_ids: List[str]) -> List[Parameter]:
        """Extract all parameters (base placeholders + option params)."""
        ...
```

### 5. ToolContext

Central place for tool name, options registry, and defaults. Reduces passing dicts through layers.

```python
# src/core/tool_context.py (or in BaseTool)
class ToolContext:
    def __init__(self, tool_name: str, options: List[CommandOption], base_command_default: str = ""):
        self.tool_name = tool_name
        self._options = {o.id: o for o in options}
        self.base_command_default = base_command_default

    def get_builder(self) -> CommandTemplateBuilder:
        return CommandTemplateBuilder(self._options)
```

### 6. Template Resolution vs. Parameter Substitution

**Two-step flow:**

1. **Resolve template:** `command.get_template(builder) -> str` – final template string from flat or composed
2. **Substitute params:** `_substitute(template, params) -> str` – pure string replacement

```python
def get_template(self, builder: Optional[CommandTemplateBuilder] = None) -> str:
    if self.source is ComposedTemplate:
        return builder.build(self.source.base_command, self.source.option_ids)
    return self.source.template

def render(self, params: Dict[str, str], builder: Optional[CommandTemplateBuilder] = None) -> str:
    template = self.get_template(builder)
    return self._substitute(template, params)
```

### 7. Command.from_generated() Factory

For "Store as full command" – keeps logic out of gen.py:

```python
@classmethod
def from_generated(cls, template: str, params_used: Dict[str, str],
                  id: str, name: str, explanation: str = "") -> 'Command':
    """Build Command from generated result. Extracts params from template."""
    ...
```

### 8. Where options live

**Recommendation:** Tool-level – each tool YAML has `command_options:` (or `sub_commands:` for backward compat) section.

### 9. CommandOption Schema

For validation at load time:

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| id | yes | str | Unique per tool |
| flag | yes | str | e.g. "-sV", "--script" |
| description | yes | str | Human-readable |
| parameter | no | Parameter | If present, option has a param placeholder |

---

## YAML Structure (nmap example)

```yaml
# data/commands/nmap.yaml
tool: nmap
command_options:  # or sub_commands for YAML backward compat
  - id: sV
    flag: "-sV"
    description: "Version detection"
  - id: sC
    flag: "-sC"
    description: "Default script scan"
  - id: ports
    flag: "-p"
    description: "Port specification"
    parameter:
      name: ports
      description: "Port spec (e.g., 80,443)"
      required: false
      default: ""
  - id: script
    flag: "--script"
    description: "NSE script(s)"
    parameter:
      name: script
      description: "Script name(s)"
      required: false
      default: ""
commands:
  - id: version-script-scan
    name: "Version + Script Scan"
    base_command: "nmap {target}"
    option_ids: [sV, sC, ports, script]  # or sub_command_ids
    explanation: "Combines version and script scanning with port selection"
    parameters: []  # Derived from base + options
    tags: [scanning, version, script]
```

---

## Implementation Phases

### Phase 1: Core models and abstractions

| Step | Task | Files |
|------|------|-------|
| 1.1 | Add `CommandOption` dataclass (id, flag, description, parameter: Optional[Parameter]) | `src/core/command.py` |
| 1.2 | Add `FlatTemplate` and `ComposedTemplate` dataclasses | `src/core/command.py` |
| 1.3 | Add `CommandTemplateBuilder` | `src/core/command_builder.py` |
| 1.4 | Add `ToolContext` | `src/core/tool_context.py` or `base_tool.py` |
| 1.5 | Extend Command: `source` (FlatTemplate | ComposedTemplate), `get_template()`, split `render()` into get_template + _substitute | `src/core/command.py` |
| 1.6 | Add `Command.from_generated()` factory | `src/core/command.py` |
| 1.7 | Update `to_dict` / `from_dict` for new fields, backward compat | `src/core/command.py` |

### Phase 2: Storage & tool loading

| Step | Task | Files |
|------|------|-------|
| 2.1 | Extend Storage to read `command_options` (or `sub_commands`) from tool YAML | `src/core/storage.py` |
| 2.2 | Add `load_tool_options(tool_name) -> List[CommandOption]` | `src/core/storage.py` |
| 2.3 | Save `command_options` when writing tool YAML | `src/core/storage.py` |
| 2.4 | BaseTool: create ToolContext from options, provide get_builder() | `src/core/base_tool.py` |
| 2.5 | CommandManager: pass tool context to Command when needed | `src/core/command_manager.py` |

### Phase 3: Add flow

| Step | Task | Files |
|------|------|-------|
| 3.1 | When adding command for tool with options: show list, toggle include/exclude | `src/cli/commands/add.py` |
| 3.2 | Build `base_command` – prompt or use tool default | `src/cli/commands/add.py` |
| 3.3 | Quick add: `--sub` or `--options sV,sC,ports` | `src/cli/commands/add.py` |
| 3.4 | Set `option_ids` and derive parameters from ToolContext | `src/cli/commands/add.py` |

### Phase 4: Edit & show

| Step | Task | Files |
|------|------|-------|
| 4.1 | Edit: allow adding/removing options | `src/cli/commands/edit.py` |
| 4.2 | Show: display options used + built template | `src/cli/commands/show.py` |
| 4.3 | Gen: pass builder to render() when command is composed | `src/cli/commands/gen.py` |

### Phase 5: Store generated as full command

**User flow:** After generating, prompt: *"Store as full command?"* If yes, save as new command.

| Step | Task | Files |
|------|------|-------|
| 5.1 | Extract `_generate_and_output()` – generate + output + clipboard | `src/cli/commands/gen.py` |
| 5.2 | Extract `_prompt_store_as_command()` – prompt, get id/name, call Command.from_generated(), save | `src/cli/commands/gen.py` |
| 5.3 | gen_command orchestrates: validate → generate → output → optionally store | `src/cli/commands/gen.py` (thin) |

**Note:** Store saves the **final template** (with `{param}` placeholders) via `Command.from_generated()`. Saved command is a regular Command (FlatTemplate).

### Phase 6: Nmap options & seed data

| Step | Task | Files |
|------|------|-------|
| 6.1 | Add `command_options` section to `nmap.yaml` | `data/commands/nmap.yaml` |
| 6.2 | Create 1–2 example composed commands | `data/commands/nmap.yaml` |
| 6.3 | Update WORKFLOW.md | `docs/WORKFLOW.md` |

---

## Migration & Backward Compatibility

- **Existing commands:** No `option_ids` / `sub_command_ids` → use `command` as FlatTemplate (current behavior)
- **Existing tools:** No `command_options` → no options UI, add/edit as today
- **YAML:** Support both `sub_commands` and `command_options` keys; support both `option_ids` and `sub_command_ids` in commands
- **Gen:** `Command.render(params, builder)` – builder optional, used when composed

---

## Open Questions

1. **Base command source:** Fixed per tool or user-defined per command?
2. **Option order:** Use order in `option_ids` or define preferred order in option defs?
3. **Other tools:** Apply to SMB, Netcat, or only nmap initially?
4. **Option management:** CLI for editing options, or YAML only?

---

## Estimate

- Phase 1: ~4 steps (core abstractions)
- Phase 2: ~2–3 steps
- Phase 3: ~2–3 steps
- Phase 4: ~1–2 steps
- Phase 5: ~2 steps (store as full command)
- Phase 6: ~1 step

**Total:** ~14–17 focused steps (aligned with "code less per step").

---

## Store as Full Command (summary)

When a command is generated (including composed options), the user can optionally **store the result as a full command**:

1. After `htb gen` outputs the generated command, prompt: *"Store as full command? [y/N]"*
2. If yes: prompt for command id and name (with suggested defaults)
3. Use `Command.from_generated(template, params, id, name)` to build Command
4. Save via `tool.add_command()`. Saved command is a regular Command (FlatTemplate).
