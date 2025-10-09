# Contributing to HoneyBaked Ham Citation Audit

## Welcome Contributors!

Thank you for your interest in contributing to the HoneyBaked Ham Citation Audit project. This document provides guidelines and instructions for contributing to the project.

## Project Overview

The HoneyBaked Ham Citation Audit is a precision methodology for analyzing brand mentions and citations across AI platforms. Our goal is to create a robust, flexible, and insightful tool for understanding generative engine optimization (GEO) strategies.

## Code of Conduct

1. Be respectful and inclusive
2. Provide constructive feedback
3. Prioritize collaboration
4. Maintain high code quality standards

## How to Contribute

### Contribution Types

1. **Bug Reports**
   - Use GitHub Issues
   - Provide detailed description
   - Include reproduction steps
   - Specify environment details

2. **Feature Requests**
   - Open a GitHub Issue
   - Describe the proposed feature
   - Explain its potential impact
   - Provide use cases

3. **Code Contributions**
   - Fork the repository
   - Create a feature branch
   - Write clean, documented code
   - Add/update tests
   - Submit a pull request

### Development Setup

1. **Prerequisites**
   - Python 3.8+
   - pip
   - Virtual environment recommended

2. **Installation Steps**
   ```bash
   # Clone the repository
   git clone https://github.com/your-username/honeybaked-ham-audit.git
   cd honeybaked-ham-audit

   # Create virtual environment
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

### Coding Standards

1. **Python Style Guide**
   - Follow PEP 8 guidelines
   - Use type hints
   - Write docstrings for all functions
   - Maximum line length: 88 characters
   - Use Black for code formatting

2. **Testing**
   - Write unit tests for new features
   - Maintain >90% test coverage
   - Use pytest for testing
   - Include mock data for API tests

3. **Documentation**
   - Update README and technical docs
   - Comment complex logic
   - Provide examples where possible

### Pull Request Process

1. Ensure all tests pass
2. Update documentation
3. Add changelog entry
4. Get code review approval
5. Squash and merge

### Commit Message Guidelines

- Use imperative mood
- Capitalize first letter
- Short, descriptive summary
- Optional detailed description

**Example:**
```
Add citation verification mechanism

- Implement URL accessibility checks
- Add content type validation
- Create fallback strategies for unreachable sources
```

## Development Workflow

### Branching Strategy
- `main`: Stable release branch
- `develop`: Integration branch
- `feature/`: New features
- `bugfix/`: Bug corrections
- `docs/`: Documentation updates

### Code Review Process
- Automated CI checks
- Minimum 1 code review required
- Discuss design choices
- Provide constructive feedback

## API Key and Sensitive Information

- Never commit API keys
- Use `.env` for local configuration
- Use environment variables in production
- Rotate keys regularly

## Reporting Security Issues

- Email: [security@project.com]
- Do not open public issues for security vulnerabilities
- Provide detailed, responsible disclosure

## Community and Support

- Join our [Discord/Slack] channel
- Weekly community calls
- Contribution office hours

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Recognized in release notes
- Potentially invited to core team

## License

By contributing, you agree to license your contributions under the project's [LICENSE] file.

## Questions?

Open an issue or contact [maintainer email/contact].

Happy Contributing! 🚀
