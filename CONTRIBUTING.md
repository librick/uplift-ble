# Contributing to uplift-ble

Thank you for your interest in improving **uplift-ble**!

Contributions are welcome, including but not limited to:

- Bug reports
- Feature requests
- Writing or editing documentation
- Code changes, including bug fixes and new features

## Safety

This library controls heavy, motorized desks; treat every code change as safety‑critical. Write defensively, validate all inputs, handle errors and timeouts explicitly, and always include a clear "stop" or fallback action to prevent uncontrolled motion. Imagine there’s a child crawling underneath.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you agree to abide by its terms.

## Reporting Issues

1. Search for existing issues on [GitHub Issues](https://github.com/librick/uplift-ble/issues).

1. If none match, open a new issue and include:

   - A clear title and description
   - Steps to reproduce (with minimal code example if applicable)
   - Expected vs. actual behavior
   - Version of `uplift-ble` and Python used

## Development Setup

See README.md for setup instructions.

## Branch Naming Convention

We follow a structured branch naming convention. All branch names must:

- Use one of these prefixes: `feat/`, `fix/`, `chore/`, or `release/`
- Use lowercase only
- Use hyphens to separate words
- Be 60 characters in length or less

### Examples

✅ **Valid branch names:**

- `feat/add-bluetooth-retry`
- `feat/2fa-authentication`
- `fix/memory-leak`
- `chore/update-dependencies`
- `release/v1.0.0`

❌ **Invalid branch names:**

- `feature/add-bluetooth` (use `feat` not `feature`)
- `feat/Add-Bluetooth` (no uppercase)
- `fix/bug-` (cannot end with dash)

### Branch Types

- **feat/** - New features or enhancements
- **fix/** - Bug fixes
- **chore/** - Maintenance, dependencies, configs, refactoring
- **release/** - Release branches (must use format `release/vX.Y.Z`)

## Commit Message Format

All commit messages must follow a format loosely based on [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/). Messages must be of the form `<type>: <message>`, and contain an optional body.

### Rules

- Type must be one of: `feat`, `fix`, or `chore`
- Message must be all lowercase
- Message can include spaces, dashes, and commas
- Maximum 72 characters for the subject line
- Use present tense ("add feature" not "added feature")

### Examples

✅ **Valid commit messages:**

```
feat: add bluetooth connection retry
fix: resolve memory leak in event handler
chore: update dependencies
chore: bump version to v1.0.0
```

❌ **Invalid commit messages:**

```
Add new feature              (missing type prefix)
feat: added new feature      (use present tense)
feat: Add new feature        (message must be lowercase)
feature: add new feature     (use 'feat' not 'feature')
```

### Commit Body

We encourage you to provide additional details in the commit body.

## Testing

Run the full test suite with:

```bash
python3 -m pytest -v
```

Consider adding tests for any new features or bug fixes.

## Pull Request Process

1. Create a **topic branch** following our naming convention:

   ```bash
   git checkout -b feat/my-new-feature
   ```

1. Write commits following our format:

   ```bash
   git commit -m "feat: add bluetooth retry logic"
   ```

1. Push your branch:

   ```bash
   git push origin feat/my-new-feature
   ```

1. Open a **Pull Request** against `main` on GitHub.

1. Ensure all checks pass:

   - Branch name validation
   - Commit message validation
   - Tests
   - Any other CI checks

1. Respond to review feedback; maintainers will merge once approved.

Thank you for contributing!
