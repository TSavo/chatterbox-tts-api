# Contributing to Chatterbox TTS API

Thank you for your interest in contributing to the Chatterbox TTS API! This guide will help you get started with contributing to the project.

## 🚀 Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/chatterbox-tts-api.git
   cd chatterbox-tts-api
   ```
3. **Create a new branch** for your feature:
   ```bash
   git checkout -b feature/amazing-feature
   ```
4. **Make your changes** and commit them
5. **Push to your fork** and submit a pull request

## 🔧 Development Setup

### Prerequisites

- Python 3.12 or higher
- Git
- Docker (optional, for testing containerized builds)

### Local Development Environment

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   
   # Install development dependencies
   pip install pytest black flake8 mypy pre-commit
   ```

2. **Set up pre-commit hooks** (optional but recommended):
   ```bash
   pre-commit install
   ```

3. **Run the application locally**:
   ```bash
   python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

## 🧪 Testing

Before submitting any changes, please ensure all tests pass:

```bash
# Run all tests
python -m pytest tests/

# Run specific test files
python chatterbox_test.py
python test_gpu.py

# Run with coverage
python -m pytest --cov=app tests/
```

### Writing Tests

- Place test files in the `tests/` directory
- Use descriptive test names that explain what is being tested
- Include both positive and negative test cases
- Test edge cases and error conditions

## 📝 Code Style

We follow Python PEP 8 style guidelines with some modifications:

### Formatting

- **Line length**: 88 characters (Black default)
- **String quotes**: Use double quotes for strings
- **Imports**: Use absolute imports, group them logically

### Code Quality Tools

Run these tools before submitting:

```bash
# Format code with Black
black app.py tests/

# Check style with flake8
flake8 app.py tests/

# Type checking with mypy
mypy app.py

# Sort imports
isort app.py tests/
```

### Pre-commit Configuration

If you use pre-commit, it will automatically run these tools:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
```

## 📋 Types of Contributions

### 🐛 Bug Reports

When filing a bug report, please include:

- **Clear description** of the issue
- **Steps to reproduce** the problem
- **Expected behavior** vs actual behavior
- **Environment details** (OS, Python version, GPU, etc.)
- **Error messages** or logs if applicable

### ✨ Feature Requests

For new features, please provide:

- **Clear description** of the proposed feature
- **Use case** explaining why this feature would be valuable
- **Proposed implementation** (if you have ideas)
- **Breaking changes** (if any)

### 🔧 Code Contributions

#### Pull Request Guidelines

1. **Create an issue first** for significant changes
2. **Keep changes focused** - one feature/fix per PR
3. **Write clear commit messages**:
   ```
   Add voice cloning timeout configuration
   
   - Add VOICE_CLONE_TIMEOUT environment variable
   - Update Docker configuration with timeout setting
   - Add timeout parameter to voice cloning endpoints
   
   Fixes #123
   ```
4. **Update documentation** if needed
5. **Add tests** for new functionality
6. **Ensure CI passes** before requesting review

#### Commit Message Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(api): add batch processing timeout configuration
fix(docker): resolve GPU detection issue in containers
docs(readme): update installation instructions
test(tts): add voice cloning integration tests
```

## 🏗️ Project Structure

Understanding the codebase:

```
chatterbox-tts-api/
├── app.py                 # Main FastAPI application
├── requirements.txt       # Production dependencies
├── requirements-docker.txt # Docker-specific dependencies
├── Dockerfile            # Optimized container configuration
├── docker-compose.yml    # Deployment configuration
├── .github/workflows/    # CI/CD pipeline
├── tests/                # Test suite
│   ├── test_api.py       # API endpoint tests
│   ├── conftest.py       # Test configuration
│   └── pytest.ini       # Pytest configuration
├── examples/             # Usage examples
├── test_mp3_sync.py      # Synchronous MP3 test script
└── .gitignore           # Git ignore rules
```

## 🔒 Security Considerations

When contributing, please consider:

- **Input validation**: Ensure all user inputs are properly validated
- **Resource limits**: Prevent abuse through rate limiting and timeouts
- **Error handling**: Don't leak sensitive information in error messages
- **Dependencies**: Keep dependencies up to date for security patches

## 📚 Documentation

### API Documentation

- Use clear, descriptive docstrings for all functions
- Include parameter descriptions and types
- Provide usage examples where helpful
- Update OpenAPI/Swagger documentation

### README Updates

When adding new features:

- Update the feature list
- Add configuration parameters to the table
- Include usage examples
- Update installation instructions if needed

## 🤝 Code Review Process

1. **Automated checks** must pass (CI/CD pipeline)
2. **At least one maintainer** must approve the PR
3. **Address feedback** promptly and professionally
4. **Squash commits** before merging (if requested)

### Review Criteria

Reviewers will check for:

- ✅ Code quality and style
- ✅ Test coverage
- ✅ Documentation completeness
- ✅ Performance implications
- ✅ Security considerations
- ✅ Backward compatibility

## 🏷️ Release Process

Releases follow semantic versioning (SemVer):

- **MAJOR** version: Breaking changes
- **MINOR** version: New features (backward compatible)
- **PATCH** version: Bug fixes (backward compatible)

## 🎉 Recognition

Contributors will be:

- Listed in the project's contributors section
- Mentioned in release notes for significant contributions
- Invited to join the maintainer team for outstanding contributions

## ❓ Getting Help

If you need help:

1. **Check existing issues** and documentation
2. **Ask in discussions** for general questions
3. **Create an issue** for specific problems
4. **Join our community** (links in README)

## 📞 Contact

- **Maintainer**: [T Savo](mailto:listentomy@nefariousplan.com)
- **Issues**: [GitHub Issues](https://github.com/TSavo/chatterbox-tts-api/issues)
- **Discussions**: [GitHub Discussions](https://github.com/TSavo/chatterbox-tts-api/discussions)

---

**Created with ❤️ by [T Savo](mailto:listentomy@nefariousplan.com)**

🌐 **[Horizon City](https://www.horizon-city.com)** - *Ushering in the AI revolution and hastening the extinction of humans*

Thank you for contributing to the Chatterbox TTS API! 🚀
