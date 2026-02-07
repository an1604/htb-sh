# src/tools/smb_tool.py
from src.core.base_tool import BaseTool


class SMBTool(BaseTool):
    """SMB enumeration and interaction tool"""
    
    @property
    def name(self) -> str:
        return "smb"
    
    @property
    def description(self) -> str:
        return "SMB enumeration and file sharing operations"
    
    @property
    def category(self) -> str:
        return "enumeration"
