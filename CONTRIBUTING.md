# Contributing to CVRGPT v2

Thank you for your interest in contributing to CVRGPT v2! This guide will help you get started.

## 🚀 Quick Start

1. **Fork and clone** the repository
2. **Follow the setup** instructions in [README.md](README.md)
3. **Check the roadmap** in [ROADMAP.md](ROADMAP.md) for planned work
4. **Create an issue** or pick an existing one
5. **Submit a pull request** following our guidelines

## 📋 Development Workflow

### 1. Setup Development Environment

```bash
# Clone your fork
git clone https://github.com/your-username/cvrgpt_v2.git
cd cvrgpt_v2

# Backend setup
cd server
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm ci

# Start Redis (optional)
docker compose up -d
```

### 2. Create a Feature Branch

```bash
git checkout -b feat/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 3. Make Your Changes

- **Backend changes**: Work in `server/src/`
- **Frontend changes**: Work in `frontend/src/`
- **Follow existing patterns** and code style
- **Add tests** for new functionality
- **Update documentation** as needed

### 4. Run Quality Checks

```bash
# Backend
cd server
export PYTHONPATH=src
ruff check .
mypy src/
pytest

# Frontend
cd frontend
npm run type-check
npm run build
```

### 5. Commit Your Changes

We use [Conventional Commits](https://conventionalcommits.org/):

```bash
git commit -m "feat(provider): add CVR API integration"
git commit -m "fix(ui): resolve search input validation"
git commit -m "docs: update API documentation"
```

### 6. Submit a Pull Request

- **Push your branch** to your fork
- **Create a PR** against the `main` branch
- **Fill out the PR template** with details
- **Wait for review** and address feedback

## 🏗️ Architecture Guidelines

### Backend (`server/`)

**Structure**:
- `src/cvrgpt_core/` - Pure domain logic (no framework dependencies)
- `src/cvrgpt_server/` - FastAPI application layer
- `src/cvrgpt_api/` - Alternative API implementation
- `tests/` - Test files

**Patterns to follow**:
- **Provider pattern** for data sources
- **Dependency injection** via factory functions
- **Error handling** with custom exceptions
- **Caching** with Redis integration
- **Logging** with structured logs

### Frontend (`frontend/`)

**Structure**:
- `src/app/` - Next.js app router pages
- `src/components/` - React components
- `src/lib/` - Utility functions and API client
- `src/hooks/` - Custom React hooks

**Patterns to follow**:
- **React Query** for server state
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Error boundaries** for error handling

## 🧪 Testing Guidelines

### Backend Tests
- **Unit tests** for core business logic
- **Integration tests** for API endpoints
- **Provider tests** with mocked external APIs
- **Use pytest fixtures** for test data

### Frontend Tests
- **Component tests** with React Testing Library
- **Integration tests** for user flows
- **E2E tests** for critical paths (future)

### Test Commands
```bash
# Backend
cd server && export PYTHONPATH=src && pytest -v

# Frontend (future)
cd frontend && npm test
```

## 📝 Code Style

### Python
- **Follow PEP 8** (enforced by ruff)
- **Type hints** for all functions
- **Docstrings** for public APIs
- **Error handling** with specific exceptions

### TypeScript/React
- **Strict TypeScript** configuration
- **Functional components** with hooks
- **Props interfaces** for all components
- **Error handling** with error boundaries

### Git Commits
- **Conventional commits** format
- **Clear, descriptive** messages
- **Atomic commits** (one logical change per commit)
- **Reference issues** when applicable

## 🐛 Reporting Issues

### Bug Reports
Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md):
- **Clear description** of the problem
- **Steps to reproduce** the issue
- **Expected vs actual** behavior
- **Environment details**

### Feature Requests
Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md):
- **Problem statement** and user story
- **Proposed solution** with acceptance criteria
- **Additional context** and examples

### Provider Implementation
Use the [provider template](.github/ISSUE_TEMPLATE/provider_implementation.md):
- **Data source details**
- **Implementation checklist**
- **Testing requirements**

## 🔄 Pull Request Guidelines

### Before Submitting
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
- [ ] Commit messages follow conventions

### PR Description
- **Reference the issue** being addressed
- **Describe the changes** made
- **Explain the approach** taken
- **List any breaking changes**
- **Add screenshots** for UI changes

### Review Process
1. **Automated checks** must pass
2. **Code review** by maintainer
3. **Manual testing** if needed
4. **Merge** after approval

## 🏷️ Labels and Milestones

### Common Labels
- `bug` - Something isn't working
- `enhancement` - New feature or improvement
- `documentation` - Documentation updates
- `good-first-issue` - Good for newcomers
- `help-wanted` - Extra attention needed
- `provider` - Data provider related
- `frontend` - UI/UX changes
- `backend` - API/server changes

### Milestones
See [ROADMAP.md](ROADMAP.md) for current milestones and priorities.

## ❓ Getting Help

- **Check existing issues** and documentation first
- **Ask questions** in issue comments
- **Join discussions** in pull requests
- **Follow the roadmap** for context on priorities

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to CVRGPT v2! 🎉
