# tests/test_flow_script_generator.py
"""Tests for FlowScriptGenerator."""

import pytest
from pathlib import Path

from src.core.storage import Storage
from src.core.command_manager import CommandManager
from src.core.flow_script_generator import FlowScriptGenerator
from src.core.flow import Flow, FlowStep
from src.core.command import Command, Parameter
from tests.test_base_tool import TestTool


@pytest.fixture
def command_manager_with_tool(storage, sample_command):
    """CommandManager with one registered tool and one command."""
    manager = CommandManager(storage)
    manager.register_tool(TestTool)
    tool = manager.get_tool("test-tool")
    assert tool is not None
    tool.add_command(sample_command)
    return manager


@pytest.fixture
def flow_with_one_step():
    """Flow that references test-tool:basic-scan with {target}."""
    step = FlowStep(
        id="scan",
        command_ref="test-tool:basic-scan",
        parameters={"target": "{target}"},
        description="Run basic scan",
    )
    return Flow(
        id="test-flow",
        name="Test Flow",
        description="A flow with one scan step",
        steps=[step],
        flow_parameters=[Parameter(name="target", description="Target IP", required=True)],
        tags=["test"],
        default_format="bash",
        add_error_handling=True,
        add_comments=True,
    )


class TestFlowScriptGenerator:
    """Test FlowScriptGenerator."""

    def test_preview_commands_resolves_params(
        self, command_manager_with_tool, flow_with_one_step
    ):
        """Test preview_commands returns rendered command strings."""
        gen = FlowScriptGenerator(command_manager_with_tool)
        commands = gen.preview_commands(flow_with_one_step, {"target": "10.10.10.5"})
        assert len(commands) == 1
        assert commands[0] == "nmap 10.10.10.5"

    def test_preview_commands_multiple_steps(
        self, command_manager_with_tool, storage, sample_command
    ):
        """Test preview_commands with multiple steps."""
        # Add another command to the tool
        tool = command_manager_with_tool.get_tool("test-tool")
        cmd2 = Command(
            id="version-scan",
            name="Version Scan",
            command="nmap -sV {target}",
            explanation="Version detection",
            parameters=[Parameter(name="target", description="Target", required=True)],
        )
        tool.add_command(cmd2)
        steps = [
            FlowStep("s1", "test-tool:basic-scan", {"target": "{target}"}),
            FlowStep("s2", "test-tool:version-scan", {"target": "{target}"}),
        ]
        flow = Flow(
            id="multi",
            name="Multi",
            description="Two steps",
            steps=steps,
            flow_parameters=[Parameter(name="target", description="IP", required=True)],
        )
        gen = FlowScriptGenerator(command_manager_with_tool)
        commands = gen.preview_commands(flow, {"target": "192.168.1.1"})
        assert len(commands) == 2
        assert commands[0] == "nmap 192.168.1.1"
        assert commands[1] == "nmap -sV 192.168.1.1"

    def test_preview_commands_uses_flow_param_defaults(
        self, command_manager_with_tool, flow_with_one_step
    ):
        """Test that missing flow params get defaults from flow.flow_parameters."""
        flow = Flow(
            id="f",
            name="F",
            description="F",
            steps=flow_with_one_step.steps,
            flow_parameters=[
                Parameter(name="target", description="IP", required=False, default="127.0.0.1"),
            ],
        )
        gen = FlowScriptGenerator(command_manager_with_tool)
        commands = gen.preview_commands(flow, {})
        assert len(commands) == 1
        assert commands[0] == "nmap 127.0.0.1"

    def test_generate_script_bash_contains_expected(
        self, command_manager_with_tool, flow_with_one_step
    ):
        """Test generate_script bash contains shebang, flow name, and command."""
        gen = FlowScriptGenerator(command_manager_with_tool)
        script = gen.generate_script(flow_with_one_step, {"target": "10.10.10.5"}, format="bash")
        assert script.startswith("#!/bin/bash")
        assert "Flow: Test Flow" in script
        assert "set -e" in script
        assert "nmap 10.10.10.5" in script
        assert "Flow completed successfully" in script

    def test_generate_script_python_contains_expected(
        self, command_manager_with_tool, flow_with_one_step
    ):
        """Test generate_script python contains shebang, docstring, and command."""
        gen = FlowScriptGenerator(command_manager_with_tool)
        script = gen.generate_script(
            flow_with_one_step, {"target": "10.10.10.5"}, format="python"
        )
        assert script.startswith("#!/usr/bin/env python3")
        assert "Flow: Test Flow" in script
        assert "subprocess" in script
        assert "run_command" in script
        assert "nmap 10.10.10.5" in script
        assert "if __name__" in script

    def test_save_script_writes_file(
        self, command_manager_with_tool, flow_with_one_step, temp_dir
    ):
        """Test save_script creates file with correct content."""
        gen = FlowScriptGenerator(command_manager_with_tool)
        script = gen.generate_script(flow_with_one_step, {"target": "1.2.3.4"}, format="bash")
        path = temp_dir / "out.sh"
        gen.save_script(script, path, make_executable=False)
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert content == script
        assert "nmap 1.2.3.4" in content

    def test_save_script_creates_parent_dirs(
        self, command_manager_with_tool, flow_with_one_step, temp_dir
    ):
        """Test save_script creates parent directories."""
        gen = FlowScriptGenerator(command_manager_with_tool)
        script = gen.generate_script(flow_with_one_step, {"target": "1.2.3.4"}, format="bash")
        path = temp_dir / "sub" / "dir" / "script.sh"
        gen.save_script(script, path)
        assert path.exists()
        assert path.read_text(encoding="utf-8") == script
