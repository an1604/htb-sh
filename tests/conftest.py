# tests/conftest.py
"""Shared pytest fixtures for all tests"""

import pytest
import tempfile
import shutil
from pathlib import Path
from src.core.storage import Storage
from src.core.command import Command, Parameter, Example


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    # Cleanup after test
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def storage(temp_dir):
    """Create a Storage instance with temporary directory (commands and flows under temp_dir)"""
    return Storage(temp_dir, flows_dir=temp_dir / "flows")


@pytest.fixture
def sample_parameter():
    """Create a sample parameter for testing"""
    return Parameter(
        name="target",
        description="Target IP address or hostname",
        required=True
    )


@pytest.fixture
def sample_optional_parameter():
    """Create a sample optional parameter with default"""
    return Parameter(
        name="ports",
        description="Port specification",
        required=False,
        default="-p 80,443"
    )


@pytest.fixture
def sample_example():
    """Create a sample example for testing"""
    return Example(
        input="nmap -sV 192.168.1.1",
        output="22/tcp  open  ssh     OpenSSH 7.6p1\n80/tcp  open  http    Apache httpd 2.4.29",
        description="Basic version scan output"
    )


@pytest.fixture
def sample_command(sample_parameter):
    """Create a sample command for testing"""
    return Command(
        id="basic-scan",
        name="Basic Port Scan",
        command="nmap {target}",
        explanation="Performs default TCP scan on top 1000 ports",
        parameters=[sample_parameter],
        tags=["basic", "scanning"],
        notes="Default scan without root privileges"
    )


# --- Flow fixtures ---
@pytest.fixture
def sample_flow_step():
    """Create a sample FlowStep for testing"""
    from src.core.flow import FlowStep
    return FlowStep(
        id="list-shares",
        command_ref="smbclient:lists-the-available-smb-shares",
        parameters={"host": "{target}"},
        description="List all SMB shares",
        notes="Run first",
    )


@pytest.fixture
def sample_flow(sample_flow_step):
    """Create a sample Flow for testing"""
    from src.core.flow import Flow
    from src.core.command import Parameter
    return Flow(
        id="smb-enumeration",
        name="SMB Enumeration",
        description="List shares and connect",
        steps=[sample_flow_step],
        flow_parameters=[
            Parameter(name="target", description="Target IP", required=True),
            Parameter(name="username", description="Username", required=False, default="guest"),
        ],
        tags=["enumeration", "smb"],
        notes="Test flow",
        default_format="bash",
        add_error_handling=True,
        add_comments=True,
    )
