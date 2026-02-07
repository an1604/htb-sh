"""Dynamic tool - loads from YAML, configurable via constructor"""

from src.core.base_tool import BaseTool


class DynamicTool(BaseTool):
    """Tool with configurable name, description, category (for user-added tools)"""

    def __init__(self, storage, name: str, description: str, category: str = "misc"):
        self._name = name
        self._description = description
        self._category = category
        super().__init__(storage)

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def category(self) -> str:
        return self._category
