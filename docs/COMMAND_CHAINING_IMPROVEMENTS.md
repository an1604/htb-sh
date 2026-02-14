# Command Chaining - Abstraction & Clean Code Suggestions

A review of [COMMAND_CHAINING_PLAN.md](COMMAND_CHAINING_PLAN.md) with suggested improvements.

---

## 1. Abstraction: Command Builder Service

**Current:** `build_template(command, sub_command_defs)` is procedural logic scattered or embedded in Command.

**Suggestion:** Introduce a **CommandTemplateBuilder** (or `CommandComposer`) that owns template construction:

```python
# src/core/command_builder.py
class CommandTemplateBuilder:
    """Builds command template from base + sub-commands. Single responsibility."""

    def __init__(self, sub_commands: Dict[str, SubCommand]):
        self._sub_commands = sub_commands

    def build(self, base_command: str, sub_command_ids: List[str]) -> str:
        """Build full template. Returns template string with {param} placeholders."""
        ...

    def get_parameters(self, base_command: str, sub_command_ids: List[str]) -> List[Parameter]:
        """Extract all parameters (base + sub-command params)."""
        ...
```

**Benefits:** Command stays a data model; build logic is testable in isolation; easy to swap strategies (e.g. different ordering rules per tool).

---

## 2. Abstraction: SubCommand as Parameter Source

**Current:** SubCommand has `has_param`, `param_name`, `param_description`, etc. – overlaps with `Parameter`.

**Suggestion:** Unify parameter representation. SubCommand either:
- **Option A:** Has an optional `parameter: Parameter` (reuse existing model)
- **Option B:** Implements a small protocol `to_parameter() -> Optional[Parameter]`

```python
@dataclass
class SubCommand:
    id: str
    flag: str
    description: str
    parameter: Optional[Parameter] = None  # None = no param (flag-only)
```

**Benefits:** One source of truth for param metadata; no duplication between SubCommand and Parameter; `Parameter` stays the single param model.

---

## 3. Abstraction: CommandSource Interface

**Current:** Command can be either "flat" (single template) or "composed" (base + sub_command_ids). Logic branches in multiple places.

**Suggestion:** Introduce a **CommandSource** abstraction (or use a small strategy):

```python
# Command has a "source" – either FlatTemplate or ComposedTemplate
@dataclass
class FlatTemplate:
    template: str

@dataclass
class ComposedTemplate:
    base_command: str
    sub_command_ids: List[str]

# Command gets:
# source: Union[FlatTemplate, ComposedTemplate]
# When source is FlatTemplate → use template as-is (backward compat)
# When source is ComposedTemplate → delegate to CommandTemplateBuilder
```

**Benefits:** Clear branching; no implicit "if sub_command_ids then X else Y" scattered in code; easy to add new source types later.

---

## 4. Separation: Template Resolution vs. Parameter Substitution

**Current:** `render(params)` does substitution. With composition, we also need "resolve template" (build from sub-commands).

**Suggestion:** Split into two steps:

1. **Resolve template:** `command.get_template(builder) -> str` – returns the final template string (from flat or composed)
2. **Substitute params:** `render(template, params) -> str` – pure string substitution

```python
def get_template(self, builder: CommandTemplateBuilder) -> str:
    """Resolve to final template string (delegates based on source)."""
    if self.sub_command_ids:
        return builder.build(self.base_command, self.sub_command_ids)
    return self.command

def render(self, params: Dict[str, str], builder: Optional[CommandTemplateBuilder] = None) -> str:
    template = self.get_template(builder) if builder else self.command
    return self._substitute(template, params)
```

**Benefits:** `render` stays simple; template resolution is explicit; easier to test and mock.

---

## 5. Factory for Command Creation

**Current:** "Store as full command" builds a Command from a rendered string – logic in `gen.py`.

**Suggestion:** Add a **CommandFactory** (or static factory method):

```python
# Command.from_generated(template: str, params_used: Dict[str, str]) -> Command
# Extracts param names from template, builds Parameter list from params_used
# Returns a Command ready for add_command()
```

**Benefits:** Gen command stays thin; creation logic is reusable (e.g. for import); easier to test.

---

## 6. Tool Context / SubCommand Registry

**Current:** Sub-commands are loaded per tool; Command needs them for building. Passing `sub_command_defs` around is implicit.

**Suggestion:** Introduce **ToolContext** (or keep it in BaseTool) that holds:
- Tool name
- Sub-commands registry
- Base command default (optional)

```python
class ToolContext:
    def __init__(self, tool_name: str, sub_commands: List[SubCommand], base_command_default: str = ""):
        self.tool_name = tool_name
        self._sub_commands = {s.id: s for s in sub_commands}
        self.base_command_default = base_command_default

    def get_builder(self) -> CommandTemplateBuilder:
        return CommandTemplateBuilder(self._sub_commands)
```

**Benefits:** Sub-commands and defaults live in one place; Builder gets its inputs from context; no passing dicts through multiple layers.

---

## 7. Naming: "Composed" vs "Chained"

**Current:** "Sub-command" and "chaining" are used. "Chaining" often implies sequential execution (cmd1 | cmd2).

**Suggestion:** Use **"composed"** or **"composite"** for combining flags into one command:
- `ComposedCommand` or `CompositeCommand` for commands built from sub-commands
- `CommandFragment` or `CommandOption` instead of `SubCommand` if "sub-command" feels ambiguous (nmap -sV is an option, not a sub-command in the shell sense)

**Benefits:** Clearer domain language; less confusion with shell piped commands.

---

## 8. Single Responsibility: Gen Command

**Current:** `gen.py` handles: params input, generation, clipboard, store-as-full-command. Multiple concerns.

**Suggestion:** Extract flows:
- `_generate_and_output(manager, command_ref, params, no_copy, print_only)` – generate + output
- `_prompt_store_as_command(manager, tool_name, generated, template, params)` – store flow
- `gen_command` orchestrates: validate → generate → output → optionally store

**Benefits:** Smaller functions; each flow testable; gen_command is a thin orchestrator.

---

## 9. Configuration: SubCommand Schema

**Current:** SubCommand YAML shape is implicit.

**Suggestion:** Add a **schema section** to the plan (or a JSON Schema / Pydantic model) for validation:

```yaml
# SubCommand schema (for validation)
# Required: id, flag, description
# If has_param/has_parameter: param_name, param_description, param_required, param_default
```

**Benefits:** Clear contract; validation at load time; fewer runtime surprises.

---

## 10. Summary: Suggested Additions to Plan

| # | Suggestion | Impact |
|---|------------|--------|
| 1 | CommandTemplateBuilder – extract build logic | High – cleaner separation |
| 2 | SubCommand.parameter instead of duplicated param fields | Medium – DRY |
| 3 | CommandSource (FlatTemplate / ComposedTemplate) | Medium – explicit branching |
| 4 | Split resolve-template vs substitute-params | Medium – testability |
| 5 | Command.from_generated() factory | Low – reusable store logic |
| 6 | ToolContext / SubCommand registry | Medium – less passing around |
| 7 | Rename to "Composed" / "CommandOption" | Low – clarity |
| 8 | Extract gen flows into helpers | Low – readability |
| 9 | SubCommand schema documentation | Low – validation |

**Priority for implementation:** 1, 2, 4 (core abstractions) then 3, 6 (structure) then 5, 8 (CLI cleanliness).
