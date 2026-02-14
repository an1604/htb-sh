# tests/test_command.py
"""Tests for Command, Parameter, and Example models"""

import pytest
from src.core.command import Command, Parameter, Example


class TestParameter:
    """Test Parameter data class"""
    
    def test_create_required_parameter(self):
        """Test creating a required parameter"""
        param = Parameter(
            name="target",
            description="Target IP address",
            required=True
        )
        
        assert param.name == "target"
        assert param.description == "Target IP address"
        assert param.required is True
        assert param.default is None
    
    def test_create_optional_parameter_with_default(self):
        """Test creating an optional parameter with default value"""
        param = Parameter(
            name="ports",
            description="Port specification",
            required=False,
            default="-p 80,443"
        )
        
        assert param.name == "ports"
        assert param.required is False
        assert param.default == "-p 80,443"


class TestExample:
    """Test Example data class"""
    
    def test_create_example_with_description(self):
        """Test creating an example with description"""
        example = Example(
            input="nmap -sV 192.168.1.1",
            output="22/tcp open ssh",
            description="Version scan"
        )
        
        assert example.input == "nmap -sV 192.168.1.1"
        assert example.output == "22/tcp open ssh"
        assert example.description == "Version scan"
    
    def test_create_example_without_description(self):
        """Test creating an example without description"""
        example = Example(
            input="nmap 192.168.1.1",
            output="scan output"
        )
        
        assert example.input == "nmap 192.168.1.1"
        assert example.output == "scan output"
        assert example.description is None


class TestCommand:
    """Test Command data class"""
    
    def test_create_command(self, sample_command):
        """Test creating a command"""
        assert sample_command.id == "basic-scan"
        assert sample_command.name == "Basic Port Scan"
        assert sample_command.command == "nmap {target}"
        assert sample_command.explanation == "Performs default TCP scan on top 1000 ports"
    
    def test_get_parameter_placeholders(self):
        """Test extracting parameter placeholders from command"""
        cmd = Command(
            id="test",
            name="Test",
            command="nmap -sV {target} {ports}",
            explanation="Test"
        )
        
        placeholders = cmd.get_parameter_placeholders()
        assert "target" in placeholders
        assert "ports" in placeholders
        assert len(placeholders) == 2
    
    def test_render_command_with_params(self, sample_parameter):
        """Test rendering command with parameters"""
        cmd = Command(
            id="test",
            name="Test",
            command="nmap {target}",
            explanation="Test",
            parameters=[sample_parameter]
        )
        
        rendered = cmd.render({"target": "192.168.1.1"})
        assert rendered == "nmap 192.168.1.1"
    
    def test_render_command_with_optional_param_provided(self, sample_optional_parameter):
        """Test rendering command with optional parameter provided"""
        param_target = Parameter(
            name="target",
            description="Target",
            required=True
        )
        cmd = Command(
            id="test",
            name="Test",
            command="nmap {ports} {target}",
            explanation="Test",
            parameters=[sample_optional_parameter, param_target]
        )
        
        # When optional parameter is provided
        rendered = cmd.render({"target": "192.168.1.1", "ports": "-p 22"})
        assert rendered == "nmap -p 22 192.168.1.1"
    
    def test_render_command_missing_required_param(self, sample_parameter):
        """Test rendering command with missing required parameter raises error"""
        cmd = Command(
            id="test",
            name="Test",
            command="nmap {target}",
            explanation="Test",
            parameters=[sample_parameter]
        )
        
        with pytest.raises(ValueError, match="Required parameter 'target' not provided"):
            cmd.render({})
    
    def test_to_dict(self, sample_parameter, sample_example):
        """Test converting command to dictionary"""
        cmd = Command(
            id="test-scan",
            name="Test Scan",
            command="nmap {target}",
            explanation="Test explanation",
            parameters=[sample_parameter],
            examples=[sample_example],
            tags=["scanning", "test"],
            notes="Test notes"
        )
        
        data = cmd.to_dict()
        
        assert data['id'] == "test-scan"
        assert data['name'] == "Test Scan"
        assert data['command'] == "nmap {target}"
        assert data['explanation'] == "Test explanation"
        assert len(data['parameters']) == 1
        assert len(data['examples']) == 1
        assert "scanning" in data['tags']
        assert data['notes'] == "Test notes"
    
    def test_from_dict(self):
        """Test creating command from dictionary"""
        data = {
            'id': 'test-scan',
            'name': 'Test Scan',
            'command': 'nmap {target}',
            'explanation': 'Test explanation',
            'parameters': [
                {
                    'name': 'target',
                    'description': 'Target IP',
                    'required': True,
                    'default': None
                }
            ],
            'examples': [
                {
                    'input': 'nmap 192.168.1.1',
                    'output': 'scan results',
                    'description': None
                }
            ],
            'tags': ['scanning'],
            'notes': 'Test notes'
        }
        
        cmd = Command.from_dict(data)
        
        assert cmd.id == 'test-scan'
        assert cmd.name == 'Test Scan'
        assert len(cmd.parameters) == 1
        assert cmd.parameters[0].name == 'target'
        assert len(cmd.examples) == 1
        assert len(cmd.tags) == 1
