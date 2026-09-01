# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2025-11-01

### Changed
- Changed license from MIT to Apache License 2.0
- Updated package metadata for PyPI publication
- Added comprehensive keywords for better discoverability
- Added Python 3.13 support
- Enhanced project URLs (Documentation, Changelog)

### Added
- LICENSE file with full Apache 2.0 text
- NOTICE file for Apache 2.0 attribution
- CHANGELOG.md for version tracking
- SECURITY.md for vulnerability reporting
- .gitignore for Python development
- Apache 2.0 license headers to all source files
- PyPI badges to README.md

## [0.2.0] - 2025-10-31

### Added
- Pluggable renderer system separating collection from rendering
- `collect_manifest()` function for pure introspection
- `render_manifest()` function with multiple output formats
- `JsonRenderer` class with customizable indentation and sorting
- `MarkdownRenderer` class for hierarchical documentation
- `CompactMarkdownRenderer` class for minimal output
- Support for custom renderer functions and classes
- Template string support for simple customization
- `Renderer` Protocol for type-safe renderer interfaces
- Comprehensive test suite (30 tests total)

### Changed
- Refactored codebase into modular structure:
  - `collector.py`: Introspection logic
  - `renderers.py`: All rendering functionality
  - `types.py`: Type definitions and protocols
  - `core.py`: Backward compatibility layer
- Improved documentation with renderer examples
- Enhanced API flexibility for user-space integrations (Jinja2, YAML, TOML)

### Deprecated
- `build_manifest()` in favor of `collect_manifest()` (still supported for backward compatibility)
- `render_manifest_list()` in favor of `render_manifest(format="markdown")` (still supported)

## [0.1.0] - 2025-10-30

### Added
- Initial release with core functionality
- `build_manifest()` function to introspect Typer/Click applications
- `write_manifest()` function to export JSON manifests to files
- `render_manifest_list()` function to generate Markdown documentation
- Support for nested command groups
- Support for both Typer and Click applications
- Complete parameter introspection (name, type, default, help, required)
- Full type annotations and mypy strict mode compliance
- Comprehensive test coverage
- README with usage examples and API documentation

[0.2.1]: https://github.com/cprima-forge/typer-manifest/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/cprima-forge/typer-manifest/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/cprima-forge/typer-manifest/releases/tag/v0.1.0
