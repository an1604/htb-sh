# src/core/storage.py
import yaml
from pathlib import Path
from typing import List, Optional
from .command import Command
from .flow import Flow


class Storage:
    """Handles YAML storage operations for commands and flows."""

    def __init__(self, data_dir: Path, flows_dir: Optional[Path] = None):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._flows_dir = Path(flows_dir) if flows_dir is not None else self.data_dir.parent / "flows"
        self._flows_dir.mkdir(parents=True, exist_ok=True)

    def get_flows_dir(self) -> Path:
        """Get directory for flow YAML files (data/flows/)."""
        return self._flows_dir

    def get_flow_file_path(self, flow_id: str) -> Path:
        """Get YAML file path for a flow (one file per flow)."""
        return self.get_flows_dir() / f"{flow_id}.yaml"

    def load_flow(self, flow_id: str) -> Optional[Flow]:
        """Load a single flow by ID. Returns None if not found."""
        file_path = self.get_flow_file_path(flow_id)
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not data:
            return None
        return Flow.from_dict(data)

    def load_flows(self) -> List[Flow]:
        """Load all flows from the flows directory."""
        flows = []
        for path in self.get_flows_dir().glob("*.yaml"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                if data and "id" in data:
                    flows.append(Flow.from_dict(data))
            except (yaml.YAMLError, KeyError, TypeError):
                continue
        return flows

    def save_flow(self, flow: Flow) -> None:
        """Save a flow to its YAML file."""
        file_path = self.get_flow_file_path(flow.id)
        data = flow.to_dict()
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    def delete_flow(self, flow_id: str) -> bool:
        """Delete a flow file. Returns True if the file existed and was removed."""
        file_path = self.get_flow_file_path(flow_id)
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def flow_exists(self, flow_id: str) -> bool:
        """Check if a flow YAML file exists."""
        return self.get_flow_file_path(flow_id).exists()

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

    def list_tool_files(self):
        """List all tool names that have YAML files"""
        return [
            p.stem for p in self.data_dir.glob("*.yaml")
        ]

    def load_tool_metadata(self, tool_name: str) -> dict:
        """Load tool metadata (description, category) from YAML"""
        file_path = self.get_tool_file_path(tool_name)
        if not file_path.exists():
            return {}
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data or {}
    
    def create_tool_file(self, tool_name: str, description: str = "",
                        category: str = "misc") -> None:
        """Create empty YAML file for new tool"""
        file_path = self.get_tool_file_path(tool_name)

        data = {
            'tool': tool_name,
            'description': description,
            'category': category,
            'commands': []
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
