# tests/test_cli_utils.py
"""Tests for CLI utility models"""

import pytest
from src.cli.utils.models import CommandDetails, ExampleDetails


class TestCommandDetails:
    """Test CommandDetails data class"""
    
    def test_create_command_details(self):
        """Test creating a CommandDetails instance"""
        cmd = CommandDetails(
            id="test-scan",
            name="Test Scan",
            command="nmap -sV {target}",
            explanation="Test scanning command"
        )
        
        assert cmd.id == "test-scan"
        assert cmd.name == "Test Scan"
        assert cmd.command == "nmap -sV {target}"
        assert cmd.explanation == "Test scanning command"
    
    def test_command_details_attributes(self):
        """Test all attributes are properly set"""
        cmd = CommandDetails(
            id="basic-scan",
            name="Basic Scan",
            command="nmap {target}",
            explanation="Basic network scan"
        )
        
        assert hasattr(cmd, 'id')
        assert hasattr(cmd, 'name')
        assert hasattr(cmd, 'command')
        assert hasattr(cmd, 'explanation')


class TestExampleDetails:
    """Test ExampleDetails data class"""
    
    def test_create_example_details_with_description(self):
        """Test creating ExampleDetails with description"""
        example = ExampleDetails(
            input="nmap -sV 192.168.1.1",
            output="PORT    STATE SERVICE\n22/tcp  open  ssh",
            description="Basic version scan"
        )
        
        assert example.input == "nmap -sV 192.168.1.1"
        assert "22/tcp" in example.output
        assert example.description == "Basic version scan"
    
    def test_create_example_details_without_description(self):
        """Test creating ExampleDetails without description"""
        example = ExampleDetails(
            input="nmap 192.168.1.1",
            output="Nmap scan report"
        )
        
        assert example.input == "nmap 192.168.1.1"
        assert example.output == "Nmap scan report"
        assert example.description is None
    
    def test_example_details_optional_description(self):
        """Test description defaults to None"""
        example = ExampleDetails(
            input="test input",
            output="test output"
        )
        
        assert example.description is None
