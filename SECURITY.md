# Security Policy

## Supported Versions

We actively support the following versions of typer-manifest with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :x:                |

## Reporting a Vulnerability

We take the security of typer-manifest seriously. If you discover a security vulnerability, please follow these steps:

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities by:

1. **Email**: Send a detailed description to the maintainer via the contact information in the project's `pyproject.toml` or GitHub profile
2. **GitHub Security Advisories**: Use the [GitHub Security Advisory](https://github.com/cprima-forge/typer-manifest/security/advisories/new) feature to privately report vulnerabilities

### What to Include

Please include the following information in your report:

- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### Response Timeline

- **Initial Response**: We will acknowledge your report within 48 hours
- **Status Update**: We will provide a more detailed response within 7 days, indicating the next steps
- **Fix Timeline**: We aim to release a fix within 30 days of the initial report, depending on complexity
- **Disclosure**: We request that you do not publicly disclose the vulnerability until we have released a fix

### After Reporting

- We will keep you informed of our progress toward resolving the issue
- We may ask for additional information or guidance
- Once the vulnerability is fixed, we will publicly acknowledge your responsible disclosure (unless you prefer to remain anonymous)

## Security Best Practices

When using typer-manifest:

1. **Keep Updated**: Always use the latest version to benefit from security patches
2. **Dependency Scanning**: Regularly scan your dependencies for known vulnerabilities
3. **Input Validation**: If exposing manifests publicly, consider sanitizing sensitive help text or parameter names
4. **Least Privilege**: Run CLI introspection with minimal necessary permissions

## Scope

This security policy applies to:

- The typer-manifest package itself (`typer-manifest` on PyPI)
- Code in the main repository at https://github.com/cprima-forge/typer-manifest

Out of scope:

- Third-party dependencies (report to their respective maintainers)
- Applications built using typer-manifest (unless the vulnerability is in typer-manifest itself)

## Attribution

We appreciate the security research community and will acknowledge researchers who responsibly disclose vulnerabilities in our release notes and security advisories.

Thank you for helping keep typer-manifest and its users safe!
