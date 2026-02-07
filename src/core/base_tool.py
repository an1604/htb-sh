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
