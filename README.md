# typer-manifest

[![PyPI version](https://badge.fury.io/py/typer-manifest.svg)](https://pypi.org/project/typer-manifest/)
[![Python versions](https://img.shields.io/pypi/pyversions/typer-manifest.svg)](https://pypi.org/project/typer-manifest/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Export [Typer](https://github.com/fastapi/typer) CLI structures as machine-readable manifests.

This lightweight utility walks a Typer (Click-based) application and emits a JSON document describing all commands, subcommands, and parameters — useful for documentation, testing, and automated CLI introspection.

## Features

- 🔌 **Pluggable Renderers**: Separate collection from rendering for maximum flexibility
- 📋 **JSON Export**: Generate complete CLI structure as JSON
- 📝 **Markdown Rendering**: Create human-readable documentation
- 🎨 **Custom Formats**: Use functions, classes, or templates for custom output
- 🔍 **Deep Introspection**: Captures commands, subcommands, parameters, types, defaults, and help text
- ⚡ **Typer & Click Support**: Works with both Typer and Click applications
- 🎯 **Fully Typed**: Complete type annotations for better IDE support
- 🪶 **Zero Extra Dependencies**: Core stays lightweight, integrate Jinja2/YAML in your project

## Installation

```bash
pip install typer-manifest
```

## Quick Start

### Basic Usage

```python
from typer_manifest import build_manifest, write_manifest
import typer

app = typer.Typer()

@app.command()
def hello(name: str = typer.Option("World", help="Name to greet")):
    """Say hello to someone."""
    print(f"Hello {name}!")

@app.command()
def goodbye(name: str = typer.Option("World", help="Name to say goodbye to")):
    """Say goodbye to someone."""
    print(f"Goodbye {name}!")

# Generate manifest programmatically
manifest = build_manifest(app, root_command_name="myapp")
print(manifest)

# Or write directly to a file
write_manifest(app, "docs/cli-manifest.json", root_command_name="myapp")
```

### Output Format

The generated JSON manifest looks like:

```json
{
  "name": "myapp",
  "commands": [
    {
      "name": "hello",
      "path": "myapp hello",
      "help": "Say hello to someone.",
      "params": [
        {
          "name": "name",
          "opts": ["--name"],
          "help": "Name to greet",
          "required": false,
          "default": "World",
          "type": "option"
        }
      ],
      "commands": []
    },
    {
      "name": "goodbye",
      "path": "myapp goodbye",
      "help": "Say goodbye to someone.",
      "params": [
        {
          "name": "name",
          "opts": ["--name"],
          "help": "Name to say goodbye to",
          "required": false,
          "default": "World",
          "type": "option"
        }
      ],
      "commands": []
    }
  ]
}
```

### Markdown Documentation

Generate human-readable markdown documentation:

```python
from typer_manifest import build_manifest, render_manifest_list

manifest = build_manifest(app, root_command_name="myapp")
markdown = render_manifest_list(manifest)
print(markdown)
```

Output:

```markdown
# myapp commands
- myapp hello: Say hello to someone.
- myapp goodbye: Say goodbye to someone.
```

## Pluggable Renderers

**New in v0.2.0:** typer-manifest now separates **collection** (introspection) from **rendering** (output formatting), giving you complete control over output formats.

### Architecture

The package is organized into two independent layers:

1. **Collector** (`collect_manifest`): Walks your CLI app and returns a pure Python dictionary
2. **Renderers**: Transform the manifest dict into various output formats

### New API (Recommended)

```python
from typer_manifest import collect_manifest, render_manifest

# Collect once
manifest = collect_manifest(app, "myapp")

# Render in multiple formats
json_output = render_manifest(manifest, format="json")
markdown_output = render_manifest(manifest, format="markdown")
compact_output = render_manifest(manifest, format="compact")
```

### Built-in Renderers

**JsonRenderer** - Formatted JSON (customizable indentation):
```python
from typer_manifest import JsonRenderer, collect_manifest

manifest = collect_manifest(app)
renderer = JsonRenderer(indent=4, sort_keys=True)
output = renderer(manifest)
```

**MarkdownRenderer** - Hierarchical bullet list with help text:
```python
from typer_manifest import MarkdownRenderer

renderer = MarkdownRenderer()
output = renderer(manifest)
# Output:
# # myapp commands
# - myapp hello: Say hello
# - myapp goodbye: Say goodbye
```

**CompactMarkdownRenderer** - Command paths only, no help text:
```python
from typer_manifest import CompactMarkdownRenderer

renderer = CompactMarkdownRenderer()
output = renderer(manifest)
# Output:
# # myapp commands
# - myapp hello
# - myapp goodbye
```

### Custom Renderers

**Option 1: Simple Function**
```python
def my_custom_renderer(manifest):
    lines = [f"CLI: {manifest['name']}", "Commands:"]
    for cmd in manifest['commands']:
        lines.append(f"  • {cmd['name']}")
    return "\n".join(lines)

manifest = collect_manifest(app)
output = render_manifest(manifest, renderer=my_custom_renderer)
```

**Option 2: Renderer Class**
```python
class TableRenderer:
    """Render as a simple table."""

    def __call__(self, manifest):
        lines = ["Command | Help", "--------|-----"]
        for cmd in manifest['commands']:
            lines.append(f"{cmd['name']} | {cmd['help']}")
        return "\n".join(lines)

output = render_manifest(manifest, renderer=TableRenderer())
```

**Option 3: Template String**
```python
template = """
# CLI Documentation

Application: {{ manifest }}

Generated automatically.
"""

output = render_manifest(manifest, template=template)
```

### User-Space Integration (No Dependencies Required!)

The core package stays lightweight with **zero extra dependencies**. For advanced templating, add your preferred libraries:

**With Jinja2:**
```python
from jinja2 import Template
from typer_manifest import collect_manifest

manifest = collect_manifest(app)

template = Template("""
# {{ manifest.name }} CLI Reference

{% for cmd in manifest.commands %}
## {{ cmd.path }}

{{ cmd.help }}

**Parameters:**
{% for param in cmd.params %}
- `{{ param.name }}`: {{ param.help }} (default: {{ param.default }})
{% endfor %}
{% endfor %}
""")

print(template.render(manifest=manifest))
```

**With YAML:**
```python
import yaml
from typer_manifest import collect_manifest

manifest = collect_manifest(app)

# Custom YAML renderer
def yaml_renderer(m):
    return yaml.dump(m, default_flow_style=False)

output = render_manifest(manifest, renderer=yaml_renderer)
```

**With TOML:**
```python
import toml
from typer_manifest import collect_manifest

manifest = collect_manifest(app)

def toml_renderer(m):
    return toml.dumps(m)

output = render_manifest(manifest, renderer=toml_renderer)
```

### Renderer Protocol

Any callable that accepts a `Manifest` dict and returns a string is a valid renderer:

```python
from typing import Protocol
from typer_manifest import Manifest

class Renderer(Protocol):
    def __call__(self, manifest: Manifest) -> str:
        ...
```

This means functions, classes with `__call__`, lambdas, and any callable work automatically!

### Migration from Old API

The old API still works for backward compatibility:

```python
# Old API (still supported)
from typer_manifest import build_manifest, render_manifest_list

manifest = build_manifest(app, "myapp")
markdown = render_manifest_list(manifest)
```

New code should use:

```python
# New API (recommended)
from typer_manifest import collect_manifest, render_manifest

manifest = collect_manifest(app, "myapp")
markdown = render_manifest(manifest, format="markdown")
```

## Advanced Usage

### Nested Command Groups

```python
import click

@click.group()
def cli():
    """Database management CLI."""
    pass

@cli.group()
def db():
    """Database commands."""
    pass

@db.command()
def migrate():
    """Run database migrations."""
    pass

@db.command()
def seed():
    """Seed the database."""
    pass

from typer_manifest import build_manifest

manifest = build_manifest(cli, root_command_name="myapp")
# Captures full hierarchy: myapp -> db -> migrate/seed
```

### Click Applications

typer-manifest works seamlessly with Click applications too:

```python
import click
from typer_manifest import write_manifest

@click.command()
@click.option('--count', default=1, help='Number of greetings')
@click.option('--name', prompt='Your name', help='The person to greet')
def hello(count, name):
    """Simple program that greets NAME COUNT times."""
    for _ in range(count):
        click.echo(f'Hello, {name}!')

write_manifest(hello, "cli-manifest.json", root_command_name="hello")
```

## API Reference

### `build_manifest(app, root_command_name=None)`

Introspect a Click or Typer app and return a structured manifest.

**Parameters:**
- `app`: A Typer app or Click command object
- `root_command_name` (optional): Name for the root command. If not provided, attempts to derive from the command's name attribute

**Returns:** Dictionary containing the complete command hierarchy

### `write_manifest(app, path, root_command_name=None)`

Generate a manifest and write it to a JSON file.

**Parameters:**
- `app`: A Typer app or Click command object
- `path`: File path where the JSON manifest should be written
- `root_command_name` (optional): Name for the root command

### `render_manifest_list(manifest)`

Render a manifest as a Markdown bullet list.

**Parameters:**
- `manifest`: A manifest dictionary generated by `build_manifest()`

**Returns:** Markdown-formatted string with a hierarchical bullet list

## Use Cases

### Documentation Generation

Automatically generate CLI documentation for your projects:

```python
from typer_manifest import build_manifest, render_manifest_list
from pathlib import Path

manifest = build_manifest(app, "myapp")
markdown = render_manifest_list(manifest)

Path("docs/cli-reference.md").write_text(markdown)
```

### Testing

Validate your CLI structure in tests:

```python
def test_cli_structure():
    manifest = build_manifest(app, "myapp")

    # Ensure all expected commands exist
    command_names = [cmd["name"] for cmd in manifest["commands"]]
    assert "init" in command_names
    assert "build" in command_names

    # Validate command parameters
    build_cmd = next(c for c in manifest["commands"] if c["name"] == "build")
    param_names = [p["name"] for p in build_cmd["params"]]
    assert "output" in param_names
```

### CI/CD Integration

Track CLI changes over time by committing manifests:

```python
# generate_manifest.py
from my_cli import app
from typer_manifest import write_manifest

write_manifest(app, "cli-manifest.json", "mycli")
```

Then in CI:
```bash
python generate_manifest.py
git diff --exit-code cli-manifest.json || echo "CLI structure changed!"
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/cprima-forge/typer-manifest
cd typer-manifest

# Install with development dependencies
uv pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/ -v
```

### Type Checking

```bash
mypy src/typer_manifest
```

### Code Formatting

```bash
black src/ tests/
ruff check src/ tests/
```

## Requirements

- Python >=3.10
- typer >=0.12
- click >=8.1

## License

Copyright 2024 Christian Prior-Mamulyan

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Related Projects

- [Typer](https://typer.tiangolo.com/) - The CLI framework this tool introspects
- [Click](https://click.palletsprojects.com/) - The underlying library for Typer
