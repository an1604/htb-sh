# src/tools/nmap_tool.py
from src.core.base_tool import BaseTool


class NmapTool(BaseTool):
    """Nmap network exploration and security auditing tool"""
    
    @property
    def name(self) -> str:
        return "nmap"
    
    @property
    def description(self) -> str:
        return "Network exploration and security auditing"
    
    @property
    def category(self) -> str:
        return "scanning"
