# tests/test_flow_commands.py
"""Tests for flow CLI commands: list, show, gen, delete, search."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch

from src.cli.main import cli
from src.core.flow import Flow, FlowStep
from src.core.flow_manager import FlowManager
from src.core.command import Parameter
from tests.test_base_tool import TestTool


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def cli_manager_with_flow(storage, sample_command):
    """CommandManager with test tool, one command, and one flow saved (for flow CLI tests)."""
    from src.core.command_manager import CommandManager
    manager = CommandManager(storage)
    manager.register_tool(TestTool)
    tool = manager.get_tool("test-tool")
    assert tool is not None
    tool.add_command(sample_command)
    step = FlowStep(
        id="scan",
        command_ref="test-tool:basic-scan",
        parameters={"target": "{target}"},
        description="Run basic scan",
    )
    flow = Flow(
        id="test-flow",
        name="Test Flow",
        description="A flow with one scan step",
        steps=[step],
        flow_parameters=[Parameter(name="target", description="Target IP", required=True)],
        tags=["test", "scan"],
        default_format="bash",
    )
    flow_mgr = FlowManager(storage)
    flow_mgr.add_flow(flow)
    return manager


class TestFlowListCommand:
    """Test htb flow list."""

    @patch("src.cli.main.get_manager")
    def test_flow_list_empty(self, mock_get_manager, runner, storage):
        """flow list with no flows prints no flows message."""
        from src.core.command_manager import CommandManager
        manager = CommandManager(storage)
        manager.register_tool(TestTool)
        mock_get_manager.return_value = manager
        result = runner.invoke(cli, ["flow", "list"])
        assert result.exit_code == 0
        assert "No flows found" in result.output

    @patch("src.cli.main.get_manager")
    def test_flow_list_with_flow(self, mock_get_manager, runner, cli_manager_with_flow):
        """flow list shows saved flow."""
        mock_get_manager.return_value = cli_manager_with_flow
        result = runner.invoke(cli, ["flow", "list"])
        assert result.exit_code == 0
        assert "test-flow" in result.output
        assert "Test Flow" in result.output or "A flow with one scan step" in result.output

    @patch("src.cli.main.get_manager")
    def test_flow_list_compact(self, mock_get_manager, runner, cli_manager_with_flow):
        """flow list --compact shows one line per flow."""
        mock_get_manager.return_value = cli_manager_with_flow
        result = runner.invoke(cli, ["flow", "list", "--compact"])
        assert result.exit_code == 0
        assert "test-flow" in result.output

    @patch("src.cli.main.get_manager")
    def test_flow_list_filter_by_tag(self, mock_get_manager, runner, cli_manager_with_flow):
        """flow list --tag test returns the flow."""
        mock_get_manager.return_value = cli_manager_with_flow
        result = runner.invoke(cli, ["flow", "list", "--tag", "test"])
        assert result.exit_code == 0
        assert "test-flow" in result.output


class TestFlowShowCommand:
    """Test htb flow show."""

    @patch("src.cli.main.get_manager")
    def test_flow_show_not_found(self, mock_get_manager, runner, cli_manager_with_flow):
        """flow show with missing id prints error."""
        mock_get_manager.return_value = cli_manager_with_flow
        result = runner.invoke(cli, ["flow", "show", "no-such-flow"])
        assert result.exit_code == 0
        assert "not found" in result.output

    @patch("src.cli.main.get_manager")
    def test_flow_show_found(self, mock_get_manager, runner, cli_manager_with_flow):
        """flow show displays flow details."""
        mock_get_manager.return_value = cli_manager_with_flow
        result = runner.invoke(cli, ["flow", "show", "test-flow"])
        assert result.exit_code == 0
        assert "Test Flow" in result.output
        assert "test-flow" in result.output
        assert "test-tool:basic-scan" in result.output

    @patch("src.cli.main.get_manager")
    def test_flow_show_compact(self, mock_get_manager, runner, cli_manager_with_flow):
        """flow show --compact shows brief output."""
        mock_get_manager.return_value = cli_manager_with_flow
        result = runner.invoke(cli, ["flow", "show", "test-flow", "--compact"])
        assert result.exit_code == 0
        assert "Test Flow" in result.output
        assert "Parameters:" in result.output
        assert "Steps:" in result.output

    @patch("src.cli.main.get_manager")
    def test_flow_show_json(self, mock_get_manager, runner, cli_manager_with_flow):
        """flow show --json outputs valid JSON structure."""
        mock_get_manager.return_value = cli_manager_with_flow
        result = runner.invoke(cli, ["flow", "show", "test-flow", "--json"])
        assert result.exit_code == 0
        assert '"id": "test-flow"' in result.output
        assert '"name": "Test Flow"' in result.output


class TestFlowGenCommand:
    """Test htb flow gen."""

    @patch("src.cli.main.get_manager")
    def test_flow_gen_not_found(self, mock_get_manager, runner, cli_manager_with_flow):
        """flow gen with missing flow id prints error."""
        mock_get_manager.return_value = cli_manager_with_flow
        result = runner.invoke(cli, ["flow", "gen", "no-such-flow", "--param", "target=1.2.3.4"])
        assert result.exit_code == 0
        assert "not found" in result.output

    @patch("src.cli.main.get_manager")
    def test_flow_gen_preview(self, mock_get_manager, runner, cli_manager_with_flow):
        """flow gen --preview with --param outputs command list."""
        mock_get_manager.return_value = cli_manager_with_flow
        result = runner.invoke(
            cli,
            ["flow", "gen", "test-flow", "--param", "target=10.10.10.5", "--preview"],
        )
        assert result.exit_code == 0
        assert "nmap 10.10.10.5" in result.output
        assert "Commands in flow" in result.output

    @patch("src.cli.main.get_manager")
    def test_flow_gen_invalid_param_format(self, mock_get_manager, runner, cli_manager_with_flow):
        """flow gen with invalid param format prints error."""
        mock_get_manager.return_value = cli_manager_with_flow
        result = runner.invoke(cli, ["flow", "gen", "test-flow", "--param", "badparam"])
        assert result.exit_code == 0
        assert "Invalid param" in result.output or "name=value" in result.output

    @patch("src.cli.main.get_manager")
    def test_flow_gen_script_contains_flow_name(self, mock_get_manager, runner, cli_manager_with_flow):
        """flow gen (no --preview) outputs script containing flow name."""
        mock_get_manager.return_value = cli_manager_with_flow
        result = runner.invoke(
            cli,
            ["flow", "gen", "test-flow", "--param", "target=1.2.3.4", "--no-copy"],
        )
        assert result.exit_code == 0
        assert "Test Flow" in result.output
        assert "#!/bin/bash" in result.output
        assert "nmap 1.2.3.4" in result.output


class TestFlowDeleteCommand:
    """Test htb flow delete."""

    @patch("src.cli.main.get_manager")
    def test_flow_delete_not_found(self, mock_get_manager, runner, cli_manager_with_flow):
        """flow delete with missing id prints error."""
        mock_get_manager.return_value = cli_manager_with_flow
        result = runner.invoke(cli, ["flow", "delete", "no-such-flow", "--force"])
        assert result.exit_code == 0
        assert "not found" in result.output

    @patch("src.cli.main.get_manager")
    def test_flow_delete_success(self, mock_get_manager, runner, cli_manager_with_flow):
        """flow delete --force removes the flow."""
        mock_get_manager.return_value = cli_manager_with_flow
        result = runner.invoke(cli, ["flow", "delete", "test-flow", "--force"])
        assert result.exit_code == 0
        assert "Deleted" in result.output
        # Flow should be gone
        flow_mgr = FlowManager(cli_manager_with_flow.storage)
        assert flow_mgr.get_flow("test-flow") is None


class TestFlowSearchCommand:
    """Test htb flow search."""

    @patch("src.cli.main.get_manager")
    def test_flow_search_no_query_returns_all(self, mock_get_manager, runner, cli_manager_with_flow):
        """flow search with no query returns flows."""
        mock_get_manager.return_value = cli_manager_with_flow
        result = runner.invoke(cli, ["flow", "search"])
        assert result.exit_code == 0
        assert "test-flow" in result.output

    @patch("src.cli.main.get_manager")
    def test_flow_search_by_query(self, mock_get_manager, runner, cli_manager_with_flow):
        """flow search with query filters by match."""
        mock_get_manager.return_value = cli_manager_with_flow
        result = runner.invoke(cli, ["flow", "search", "test-flow"])
        assert result.exit_code == 0
        assert "test-flow" in result.output

    @patch("src.cli.main.get_manager")
    def test_flow_search_by_tag(self, mock_get_manager, runner, cli_manager_with_flow):
        """flow search --tag returns matching flows."""
        mock_get_manager.return_value = cli_manager_with_flow
        result = runner.invoke(cli, ["flow", "search", "--tag", "scan"])
        assert result.exit_code == 0
        assert "test-flow" in result.output

    @patch("src.cli.main.get_manager")
    def test_flow_search_compact(self, mock_get_manager, runner, cli_manager_with_flow):
        """flow search --compact shows one line per flow."""
        mock_get_manager.return_value = cli_manager_with_flow
        result = runner.invoke(cli, ["flow", "search", "--compact"])
        assert result.exit_code == 0
        assert "test-flow" in result.output
