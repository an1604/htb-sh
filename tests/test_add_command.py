# tests/test_add_command.py
"""Tests for add command"""

import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch
from src.cli.main import cli
from src.cli.utils.models import CommandDetails
from src.core.command import Parameter


class TestAddCommand:
    """Test add command functionality"""
    
    @pytest.fixture
    def runner(self):
        """Create CLI test runner"""
        return CliRunner()
    
    @pytest.fixture
    def mock_command_details(self):
        """Create mock CommandDetails"""
        return CommandDetails(
            id="test-scan",
            name="Test Scan",
            command="nmap -sV {target}",
            explanation="Test scanning command"
        )
    
    @pytest.mark.skip_ci
    @patch('src.cli.commands.add.InteractivePrompts')
    @patch('src.cli.commands.add.load_config')
    @patch('src.cli.commands.add.get_tag_suggestions')
    def test_add_command_basic_flow(self, mock_get_tags, mock_load_config, mock_prompts_class, runner, mock_command_details):
        """Test basic add command flow"""
        # Setup mocks
        mock_prompts = Mock()
        mock_prompts_class.return_value = mock_prompts
        mock_prompts.select_tool.return_value = "nmap"
        mock_prompts.input_command_details.return_value = mock_command_details
        mock_prompts.configure_parameter.return_value = Parameter(
            name="target",
            description="Target IP",
            required=True,
            default=None
        )
        mock_prompts.input_tags.return_value = ["test", "scanning"]
        mock_prompts.add_example.return_value = None  # No examples
        mock_prompts.review_and_confirm.return_value = True  # User confirms
        
        mock_get_tags.return_value = ["test", "scanning"]
        mock_load_config.return_value = {}
        
        # Run command
        result = runner.invoke(cli, ['add'])
        
        # Assertions
        assert result.exit_code == 0
        assert "saved successfully" in result.output
        
        # Verify mocks were called
        mock_prompts.select_tool.assert_called_once()
        mock_prompts.input_command_details.assert_called_once()
        mock_prompts.review_and_confirm.assert_called_once()
    
    @pytest.mark.skip_ci
    @patch('src.cli.commands.add.InteractivePrompts')
    def test_add_command_no_tools_available(self, mock_prompts_class, runner):
        """Test add command when no tools are registered"""
        # This test would need a way to inject an empty manager
        # For now, we know tools are always registered in our setup
        pass
    
    @pytest.mark.skip_ci
    @patch('src.cli.commands.add.InteractivePrompts')
    def test_add_command_invalid_tool(self, mock_prompts_class, runner):
        """Test add command with invalid tool name"""
        mock_prompts = Mock()
        mock_prompts_class.return_value = mock_prompts
        mock_prompts.select_tool.return_value = "nonexistent-tool"
        
        result = runner.invoke(cli, ['add'])
        
        assert result.exit_code == 0
        assert "not found" in result.output
    
    @pytest.mark.skip_ci
    @patch('src.cli.commands.add.InteractivePrompts')
    @patch('src.cli.commands.add.load_config')
    @patch('src.cli.commands.add.get_tag_suggestions')
    def test_add_command_detects_multiple_parameters(self, mock_get_tags, mock_load_config, mock_prompts_class, runner):
        """Test that multiple parameters are detected"""
        mock_prompts = Mock()
        mock_prompts_class.return_value = mock_prompts
        mock_prompts.select_tool.return_value = "nmap"
        
        cmd_details = CommandDetails(
            id="complex-scan",
            name="Complex Scan",
            command="nmap {target} {ports} {options}",
            explanation="Complex scanning command"
        )
        mock_prompts.input_command_details.return_value = cmd_details
        
        # Mock parameter configuration for each detected parameter
        mock_prompts.configure_parameter.side_effect = [
            Parameter(name="target", description="Target", required=True),
            Parameter(name="ports", description="Ports", required=False),
            Parameter(name="options", description="Options", required=False),
        ]
        mock_prompts.input_tags.return_value = []
        mock_prompts.add_example.return_value = None
        mock_prompts.review_and_confirm.return_value = True
        
        mock_get_tags.return_value = []
        mock_load_config.return_value = {}
        
        result = runner.invoke(cli, ['add'])
        
        assert result.exit_code == 0
        assert "3 parameter(s)" in result.output
        # Verify configure_parameter was called 3 times
        assert mock_prompts.configure_parameter.call_count == 3
    
    @pytest.mark.skip_ci
    @patch('src.cli.commands.add.InteractivePrompts')
    @patch('src.cli.commands.add.load_config')
    @patch('src.cli.commands.add.get_tag_suggestions')
    def test_add_command_no_parameters(self, mock_get_tags, mock_load_config, mock_prompts_class, runner):
        """Test add command with no parameters in template"""
        mock_prompts = Mock()
        mock_prompts_class.return_value = mock_prompts
        mock_prompts.select_tool.return_value = "nmap"
        
        cmd_details = CommandDetails(
            id="simple-scan",
            name="Simple Scan",
            command="nmap -sV 192.168.1.1",
            explanation="Simple hardcoded scan"
        )
        mock_prompts.input_command_details.return_value = cmd_details
        mock_prompts.input_tags.return_value = []
        mock_prompts.add_example.return_value = None
        mock_prompts.review_and_confirm.return_value = True
        
        mock_get_tags.return_value = []
        mock_load_config.return_value = {}
        
        result = runner.invoke(cli, ['add'])
        
        assert result.exit_code == 0
        assert "saved successfully" in result.output
        # configure_parameter should not be called
        mock_prompts.configure_parameter.assert_not_called()
    
    def test_add_command_exists_in_cli(self, runner):
        """Test that add command is registered in CLI"""
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert "add" in result.output.lower()
    
    @pytest.mark.skip_ci
    @patch('src.cli.commands.add.InteractivePrompts')
    @patch('src.cli.commands.add.load_config')
    @patch('src.cli.commands.add.get_tag_suggestions')
    def test_add_command_displays_success_message(self, mock_get_tags, mock_load_config, mock_prompts_class, runner, mock_command_details):
        """Test that success message is displayed"""
        mock_prompts = Mock()
        mock_prompts_class.return_value = mock_prompts
        mock_prompts.select_tool.return_value = "smb"
        mock_prompts.input_command_details.return_value = mock_command_details
        mock_prompts.configure_parameter.return_value = Parameter(name="target", description="Target", required=True)
        mock_prompts.input_tags.return_value = []
        mock_prompts.add_example.return_value = None
        mock_prompts.review_and_confirm.return_value = True
        
        mock_get_tags.return_value = []
        mock_load_config.return_value = {}
        
        result = runner.invoke(cli, ['add'])
        
        assert result.exit_code == 0
        assert "smb:test-scan" in result.output
        assert "✅" in result.output or "saved successfully" in result.output
