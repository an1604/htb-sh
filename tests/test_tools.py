# tests/test_tools.py
"""Tests for concrete tool implementations"""

import pytest
from src.tools import NmapTool, SMBTool, NetcatTool


class TestNmapTool:
    """Test NmapTool implementation"""
    
    @pytest.fixture
    def nmap_tool(self, storage):
        """Create NmapTool instance"""
        return NmapTool(storage)
    
    def test_name(self, nmap_tool):
        """Test tool name"""
        assert nmap_tool.name == "nmap"
    
    def test_description(self, nmap_tool):
        """Test tool description"""
        assert nmap_tool.description == "Network exploration and security auditing"
    
    def test_category(self, nmap_tool):
        """Test tool category"""
        assert nmap_tool.category == "scanning"


class TestSMBTool:
    """Test SMBTool implementation"""
    
    @pytest.fixture
    def smb_tool(self, storage):
        """Create SMBTool instance"""
        return SMBTool(storage)
    
    def test_name(self, smb_tool):
        """Test tool name"""
        assert smb_tool.name == "smb"
    
    def test_description(self, smb_tool):
        """Test tool description"""
        assert smb_tool.description == "SMB enumeration and file sharing operations"
    
    def test_category(self, smb_tool):
        """Test tool category"""
        assert smb_tool.category == "enumeration"


class TestNetcatTool:
    """Test NetcatTool implementation"""
    
    @pytest.fixture
    def netcat_tool(self, storage):
        """Create NetcatTool instance"""
        return NetcatTool(storage)
    
    def test_name(self, netcat_tool):
        """Test tool name"""
        assert netcat_tool.name == "netcat"
    
    def test_description(self, netcat_tool):
        """Test tool description"""
        assert netcat_tool.description == "Network debugging and data transfer tool"
    
    def test_category(self, netcat_tool):
        """Test tool category"""
        assert netcat_tool.category == "misc"
