# src/core/command_manager.py
from typing import List, Dict, Optional, Type
from .base_tool import BaseTool
from .storage import Storage
from src.tools.dynamic_tool import DynamicTool


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

    def register_dynamic_tool(self, name: str, description: str,
                             category: str = "misc") -> None:
        """Register a dynamic tool (user-added via tool add)"""
        tool = DynamicTool(self.storage, name, description, category)
        self._tools[name] = tool

    def load_dynamic_tools(self, exclude: List[str] = None) -> None:
        """Load tools from YAML files that are not already registered"""
        exclude = exclude or []
        for name in self.storage.list_tool_files():
            if name in self._tools or name in exclude:
                continue
            meta = self.storage.load_tool_metadata(name)
            desc = meta.get('description', '')
            cat = meta.get('category', 'misc')
            self.register_dynamic_tool(name, desc, cat)
    
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
                   category: str = None, tool: str = None) -> Dict[str, List]:
        """Search across all tools"""
        results = {}
        for tool_name, tool in self._tools.items():
            # Filter by tool if specified
            if tool and tool_name != tool:
                continue
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
