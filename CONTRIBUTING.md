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
2. If none match, open a new issue and include:

   * A clear title and description
   * Steps to reproduce (with minimal code example if applicable)
   * Expected vs. actual behavior
   * Version of `uplift-ble` and Python used

## Development Setup
See README.md for setup instructions.

## Testing

Run the full test suite with:

```bash
python3 -m pytest -v
```

Consider adding tests for any new features or bug fixes.

## Pull Request Process

1. Create a **topic branch** for your change: `git checkout -b feat/my-new-feature`
2. Commit changes in logical chunks; rebase or squash as needed.
3. Push your branch: `git push origin feat/my-new-feature`
4. Open a **Pull Request** against `main` on GitHub.
5. Ensure all checks (CI/test/lint) pass.
6. Respond to review feedback; maintainers will merge once approved.

Thank you for contributing!