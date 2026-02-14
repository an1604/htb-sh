# src/cli/utils/constants.py
"""Constants and formatting strings for CLI utilities"""

# Rich formatting colors
COLOR_HEADING = "bold cyan"
COLOR_CATEGORY = "yellow"
COLOR_LABEL = "yellow"
COLOR_SUCCESS = "green"
COLOR_ERROR = "red"
COLOR_WARNING = "yellow"

# Panel and prompt messages
MSG_AVAILABLE_TOOLS = "\n[bold cyan]Available Tools:[/bold cyan]"
MSG_COMMAND_DETAILS = "\n[bold cyan]Command Details[/bold cyan]"
MSG_CONFIGURE_PARAM = "\n[bold cyan]Configure Parameter: {}[/bold cyan]"
MSG_TAGS = "\n[bold cyan]Tags[/bold cyan]"
MSG_COMMAND_EXAMPLE = "\n[bold cyan]Command Example[/bold cyan]"
MSG_REVIEW_COMMAND = "\n[bold cyan]Review Command[/bold cyan]"

# Prompts
PROMPT_SELECT_TOOL = "\n[bold]Select tool[/bold]"
PROMPT_COMMAND_NAME = "Command Name"
PROMPT_COMMAND_ID = "Command ID"
PROMPT_COMMAND_TEMPLATE = "Command Template (use {param} for variables)"
PROMPT_EXPLANATION = "Explanation"
PROMPT_PARAM_DESC = "  Description"
PROMPT_PARAM_REQUIRED = "  Required?"
PROMPT_PARAM_DEFAULT = "  Default value (optional)"
PROMPT_TAGS_INPUT = "Tags (comma-separated)"
PROMPT_EXAMPLE_INPUT = "  Example Input"
PROMPT_EXAMPLE_OUTPUT = "  Example Output (paste, then press Enter on empty line):"
PROMPT_EXAMPLE_DESC = "  Example Description (optional)"
PROMPT_ADD_EXAMPLE = "\n[bold]Add an example?[/bold]"
PROMPT_SAVE_COMMAND = "\n[bold]Save this command?[/bold]"

# Review panel template
REVIEW_PANEL_TEMPLATE = """[yellow]Tool:[/yellow] {tool}
[yellow]ID:[/yellow] {id}
[yellow]Name:[/yellow] {name}
[yellow]Command:[/yellow] {command}
[yellow]Explanation:[/yellow] {explanation}
[yellow]Parameters:[/yellow] {param_count}
[yellow]Examples:[/yellow] {example_count}
[yellow]Tags:[/yellow] {tags}"""

# Panel titles
PANEL_TITLE_SUMMARY = "Command Summary"
PANEL_TITLE_COMMAND = "Command: {}"

# Show command display templates
SHOW_TOOL_LINE = "[bold]Tool:[/bold] {}"
SHOW_ID_LINE = "[bold]ID:[/bold] {}"
SHOW_NAME_LINE = "[bold]Name:[/bold] {}"
SHOW_COMMAND_LABEL = "[bold]Command:[/bold]"
SHOW_COMMAND_VALUE = "  {}"
SHOW_EXPLANATION_LABEL = "[bold]Explanation:[/bold]"
SHOW_EXPLANATION_VALUE = "  {}"

# Misc
TAG_SUGGESTIONS_PREFIX = "  Suggestions: "
TAG_SEPARATOR = ", "
