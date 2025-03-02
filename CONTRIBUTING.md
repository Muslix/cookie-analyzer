# Contributing to Cookie Analyzer

First off, thank you for considering contributing to Cookie Analyzer! It's people like you that make this tool better for everyone.

## Code of Conduct

Please treat all other contributors with respect and follow our standards of behavior.

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report. Following these guidelines helps maintainers understand your report, reproduce the behavior, and find related reports.

- Use a clear and descriptive title
- Describe the exact steps which reproduce the problem
- Provide specific examples to demonstrate the steps
- Describe the behavior you observed after following the steps
- Explain which behavior you expected to see instead and why
- Include screenshots if relevant

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion, including completely new features and minor improvements to existing functionality.

- Use a clear and descriptive title
- Provide a step-by-step description of the suggested enhancement
- Provide specific examples to demonstrate the enhancement
- Describe the current behavior and explain which behavior you expected to see instead
- Explain why this enhancement would be useful

### Pull Requests

- Fill in the required template
- Do not include issue numbers in the PR title
- Include screenshots and animated GIFs in your pull request whenever possible
- Follow the Python style guide
- Include tests for new features
- Document new code

## Development Workflow

### Setting Up the Development Environment

1. Fork the repository
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/cookie-analyzer.git
   cd cookie-analyzer
   ```

3. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   make install
   # or
   pip install -e .
   pip install -r requirements.txt
   ```

5. Install pre-commit hooks:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

### Making Changes

1. Create a new branch:
   ```bash
   git checkout -b feature/my-feature-name
   ```

2. Make your changes
3. Format and lint your code:
   ```bash
   make format
   make lint
   ```

4. Run tests:
   ```bash
   make test
   # or for coverage report
   make coverage
   ```

5. Commit your changes using a descriptive commit message:
   ```bash
   git add .
   git commit -m "Add feature: my feature description"
   ```

## Continuous Integration

Our project uses GitHub Actions for CI/CD. When you submit a pull request, the following checks will run:

1. **CI Workflow:** Runs tests on multiple Python versions
2. **Code Quality:** Checks formatting, linting, and static analysis
3. **Docker Build:** Tests building a Docker image of your changes
4. **Security Scanning:** Checks for vulnerabilities in the code and dependencies

Pull requests won't be merged until all CI checks pass.

## Release Process

Releases are managed through GitHub Actions:

1. A version bump is triggered via the Version Bump workflow
2. This creates a new tag and GitHub Release
3. The package is automatically published to PyPI and a Docker image is pushed to GitHub Container Registry

## Coding Conventions

### Python Style Guide

- Follow [PEP 8](https://pep8.org/) - we use Black, flake8, and pylint to enforce this
- Use type hints where possible
- Write docstrings for all classes, methods, and functions

### Testing

- Write tests for all new features
- Maintain or improve test coverage with your changes
- Use pytest for writing tests

### Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- feat: A new feature
- fix: A bug fix
- docs: Documentation only changes
- style: Changes that do not affect the meaning of the code
- refactor: A code change that neither fixes a bug nor adds a feature
- perf: A code change that improves performance
- test: Adding missing tests or correcting existing tests
- build: Changes that affect the build system or external dependencies
- ci: Changes to our CI configuration files and scripts

Example: `feat: add support for cookie consent banners`

## Documentation

- Update the README.md with details of changes to the interface
- Document new features in the code with docstrings
- Create examples for new functionality

## Thank You

Thank you for contributing to Cookie Analyzer! Your efforts help make this tool better for everyone.