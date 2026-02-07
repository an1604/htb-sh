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
    """Create a Storage instance with temporary directory"""
    return Storage(temp_dir)


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
