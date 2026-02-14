# src/tools/netcat_tool.py
from src.core.base_tool import BaseTool


class NetcatTool(BaseTool):
    """Netcat network debugging and exploration tool"""
    
    @property
    def name(self) -> str:
        return "netcat"
    
    @property
    def description(self) -> str:
        return "Network debugging and data transfer tool"
    
    @property
    def category(self) -> str:
        return "misc"
