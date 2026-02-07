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
        
        with open(file_path, 'r', encoding='utf-8') as f:
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
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
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
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
