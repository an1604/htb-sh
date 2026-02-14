# Contributing to HTB Automations

Thank you for your interest in contributing to HTB Automations! This guide will help you get started.

## Development Workflow

### Getting Started

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/htb-automations.git
   cd htb-automations
   ```

2. **Set up your development environment**
   ```bash
   # Install production dependencies
   pip install -r requirements.txt
   
   # Install development dependencies
   pip install -r requirements-dev.txt
   
   # Install in development mode
   pip install -e .
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

### Making Changes

1. **Write your code**
   - Follow existing code style and patterns
   - Add docstrings to functions and classes
   - Keep changes focused and atomic

2. **Write tests**
   - Add tests for new features in the `tests/` directory
   - Ensure existing tests still pass
   - Aim for high test coverage

3. **Run tests locally**
   ```bash
   # Run all tests
   pytest tests/ -v
   
   # Run tests with coverage
   pytest tests/ -v --cov=src --cov-report=term-missing
   
   # Run specific test file
   pytest tests/test_command.py -v
   ```

4. **Commit your changes**
   - Follow [Conventional Commits](https://www.conventionalcommits.org/) format
   - Write clear, descriptive commit messages
   
   Examples:
   ```bash
   git commit -m "feat(flows): add support for Python script generation"
   git commit -m "fix(cli): resolve parameter validation issue"
   git commit -m "docs: update installation instructions"
   ```

### Submitting a Pull Request

1. **Push your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request**
   - Go to GitHub and create a PR from your branch to `dev`
   - Provide a clear title and description
   - Reference any related issues

3. **CI/CD Checks**
   - GitHub Actions will automatically run tests against Python 3.8, 3.9, 3.10, and 3.11
   - All tests must pass before the PR can be merged
   - Check the Actions tab if tests fail

4. **Code Review**
   - Address any feedback from reviewers
   - Push additional commits to your branch as needed
   - Tests will re-run automatically

5. **Merge**
   - Once approved and all tests pass, your PR will be merged
   - PRs to `main` require at least one approval
   - PRs to `dev` can be merged once tests pass

## Branch Strategy

- `main` - Production-ready code
- `dev` - Development branch for integration
- `feature/*` - New features
- `fix/*` - Bug fixes
- `docs/*` - Documentation updates

## Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Keep functions small and focused
- Add comments for complex logic

## Testing Guidelines

- Write unit tests for all new functions and classes
- Test both success and error cases
- Use fixtures from `tests/conftest.py` when applicable
- Mock external dependencies

## Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(flows): add error handling to script generation
fix(cli): correct parameter validation for optional fields
docs: update README with new command examples
test(storage): add tests for flow persistence
```

## Need Help?

- Open an issue for bugs or feature requests
- Check existing issues before creating a new one
- Join the discussion in pull requests

Thank you for contributing!
