# Testing Strategy

**Version:** 1.0  
**Date:** February 7, 2026

---

## Overview

This document outlines the testing strategy for the HTB Command Automation Tool. Our goal is to ensure code quality, reliability, and maintainability through comprehensive automated testing.

---

## Testing Framework

- **Framework:** pytest
- **Coverage Tool:** pytest-cov (optional, for future)
- **Minimum Python Version:** 3.8+

---

## Test Structure

```
tests/
├── __init__.py
├── test_command.py           # Command, Parameter, Example models
├── test_storage.py           # YAML storage operations
├── test_base_tool.py         # BaseTool abstract class
├── test_command_manager.py   # CommandManager orchestration
├── test_tools.py             # Concrete tool implementations
├── test_cli_utils.py         # CLI utility models and constants
└── conftest.py               # Shared fixtures
```

---

## Testing Layers

### 1. Unit Tests

Test individual components in isolation:

#### Core Models (`test_command.py`)
- **Parameter class:**
  - Required vs optional parameters
  - Default values
  - Data validation

- **Example class:**
  - With and without description
  - Multi-line output handling

- **Command class:**
  - Creation and properties
  - Parameter placeholder extraction
  - Command rendering with params
  - Missing required parameter handling
  - Serialization (to_dict)
  - Deserialization (from_dict)

#### Storage Layer (`test_storage.py`)
- **Storage class:**
  - Directory creation
  - File path generation
  - Save commands to YAML
  - Load commands from YAML
  - Handle non-existent files
  - Unicode character support
  - Multiple commands per tool
  - Tool existence check

#### Tool Layer (`test_base_tool.py`)
- **BaseTool (via concrete test implementation):**
  - Tool properties (name, description, category)
  - Add command
  - Get command by ID
  - Update command
  - Delete command
  - Search by query
  - Search by tags
  - Generate command with params
  - Execute command (dry run mode)

#### Command Manager (`test_command_manager.py`)
- **CommandManager:**
  - Tool registration
  - Get tool by name
  - List tools (all and by category)
  - Get categories
  - Search across all tools
  - Get command by reference (tool:command_id)
  - Generate command by reference

#### Concrete Tools (`test_tools.py`)
- **NmapTool, SMBTool, NetcatTool:**
  - Correct name property
  - Correct description property
  - Correct category property
  - Inheritance from BaseTool

#### CLI Utilities (`test_cli_utils.py`)
- **CommandDetails model:**
  - Data structure validation
  - All required fields present

- **ExampleDetails model:**
  - With description
  - Without description (None default)

---

## Test Fixtures

### Shared Fixtures (`conftest.py`)

```python
@pytest.fixture
def temp_dir():
    """Temporary directory for file operations"""
    
@pytest.fixture
def storage(temp_dir):
    """Storage instance with temp directory"""
    
@pytest.fixture
def sample_command():
    """Sample command for testing"""
    
@pytest.fixture
def sample_parameter():
    """Sample parameter for testing"""
```

---

## Test Coverage Goals

### Phase 1: Core Foundation
- ✅ Command models: **100%** coverage
- ✅ Storage operations: **95%+** coverage
- ✅ BaseTool: **90%+** coverage
- ✅ CommandManager: **90%+** coverage

### Phase 2: Tool Implementation
- ✅ Concrete tools: **100%** coverage (simple properties)
- ✅ Tool registration: **100%** coverage

### Phase 3: CLI (Future)
- 🔄 Interactive prompts: **Manual testing** (user interaction)
- 🔄 CLI commands: **Integration tests**

---

## Test Execution

### Running Tests

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_command.py

# Run specific test
pytest tests/test_command.py::TestCommand::test_render_command_with_params

# Run with coverage (future)
pytest --cov=src --cov-report=html
```

---

## Testing Best Practices

### 1. Test Naming Convention
- Test files: `test_<module>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<what_it_tests>`

### 2. AAA Pattern (Arrange-Act-Assert)
```python
def test_example():
    # Arrange: Set up test data
    cmd = Command(id="test", name="Test", ...)
    
    # Act: Execute the operation
    result = cmd.render({"param": "value"})
    
    # Assert: Verify the outcome
    assert result == "expected output"
```

### 3. One Assertion Per Test (when possible)
- Keep tests focused and simple
- Exception: Related assertions that test the same behavior

### 4. Use Fixtures for Setup
- Avoid duplication
- Share common test data
- Clean up resources automatically

### 5. Test Edge Cases
- Empty inputs
- None values
- Missing required data
- Invalid data types
- Unicode characters
- Large datasets

### 6. Mock External Dependencies (Future)
- File system operations (for integration tests)
- User input (for CLI tests)
- Network calls (when added)

---

## Test Data

### Sample Commands
```yaml
# Basic scan
id: basic-scan
name: Basic Port Scan
command: nmap {target}
parameters:
  - name: target
    required: true

# Complex command with multiple parameters
id: version-scan
name: Service Version Detection
command: nmap -sV {target} {ports}
parameters:
  - name: target
    required: true
  - name: ports
    required: false
    default: "-p-"
```

---

## Continuous Integration (Future)

### GitHub Actions Workflow
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest -v
```

---

## Testing Phases

### Phase 1: Core Testing (Current)
- ✅ Models (Command, Parameter, Example)
- ✅ Storage layer
- ✅ BaseTool
- ✅ CommandManager
- ✅ Concrete tools

### Phase 2: Integration Testing (Future)
- Tool + Storage integration
- CommandManager + Tools integration
- End-to-end command workflow

### Phase 3: CLI Testing (Future)
- Manual testing for interactive prompts
- Automated testing for command execution
- Integration with Rich console

---

## Excluded from Automated Testing

1. **Interactive Prompts** - Require manual testing due to user interaction
2. **Rich Console Output** - Visual formatting best tested manually
3. **Clipboard Operations** - Platform-specific, manual verification
4. **Command Execution** (future feature) - Security concerns, manual testing preferred

---

## Success Criteria

- ✅ All unit tests pass
- ✅ No linting errors
- ✅ Test coverage > 85% for core modules
- ✅ Tests run in < 5 seconds
- ✅ Tests are deterministic (no flaky tests)
- ✅ Clear test documentation

---

## Maintenance

- **Update tests** when adding new features
- **Refactor tests** when refactoring code
- **Remove obsolete tests** when features are removed
- **Review test coverage** monthly
- **Keep test data realistic** and representative

---

**Status:** 📝 Strategy Approved - Ready for Implementation  
**Next Step:** Implement tests in separate testing branch
