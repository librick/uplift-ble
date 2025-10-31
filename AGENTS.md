# CLAUDE.md

This file provides guidelines for AI assistants working on this Python project.

## Language Features and Modern Python

- Always use type hints for function signatures and class attributes
- Use `|` for union types instead of `Union` (e.g., `str | int`)
- Use `<type> | None` instead of `Optional[<type>]`
- Import collection interfaces from `collections.abc` (e.g., `Iterator`, `Iterable`, `Mapping`, `Sequence`)
- Use builtin types directly for type annotations: `list`, `dict`, `set` (not `List`, `Dict`, `Set` from typing)
- Prefer `pathlib` over `os.path` for file system operations
- Use f-strings over `.format()` or `%` formatting
- Prefer async/await over callbacks for asynchronous code
- Don't use special naming conventions for async functions (e.g., no `async_` prefix)

## Code Organization

- For functions that return multiple pieces of data, prefer `@dataclass` to tuples for clarity and type safety
- Use context managers and async context managers when available and appropriate
- Place private helper functions at module-level with underscore prefix instead of using `@staticmethod` decorators

## Docstrings
- Use Google-style docstrings
- Don't document types in docstrings when you have type hints
- Private functions typically don't need docstrings

## Imports
- Import sorting should be handled by ruff
- Prefer absolute imports over relative imports
- All imports should be at the top of the file, avoid imports inside functions

## Code Quality Tools

- Use `ruff` for both linting and code formatting
- Use `codespell` to catch common spelling errors
- Use `mdformat` for formatting Markdown files

## Design Principles

- Prefer composition over inheritance
- Use dependency injection for testability and flexibility
  - Exception: Do not use dependency injection for loggers; create them directly in each module

## Logging

- Use `logger.info`, `logger.warning`, etc. instead of `print()` for application logging
- In libraries, prefer `logger.debug` over `logger.info` (keep libraries quiet by default)
- For CLI apps/scripts, write log messages to stderr, not stdout

## Testing

- Use `pytest` for unit tests
- Test behavior, not implementation details
- Prefer testing public APIs over private functions, but be pragmatic
- If code is hard to test, consider it a code smell—refactor for testability

## General Guidelines

- When editing code, don't add comments explaining changes or addressing feedback. Code should be self-documenting.
- When contributing to this project, ensure all code follows these conventions.
