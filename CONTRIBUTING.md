# Contributing to Meeting Brief Agent

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Set up the development environment

## Development Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

## Code Style

### Python
- Use `ruff` for linting and formatting
- Follow PEP 8 guidelines
- Add type hints to all functions

### TypeScript
- Use ESLint and Prettier
- Follow the existing code patterns
- Use TypeScript strict mode

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with clear commits
3. Write/update tests as needed
4. Update documentation if applicable
5. Submit a pull request

## Commit Messages

Follow conventional commits format:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation
- `refactor:` Code refactoring
- `test:` Tests

## Questions?

Open an issue or start a discussion on GitHub.
