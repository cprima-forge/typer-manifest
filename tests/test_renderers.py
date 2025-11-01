"""Tests for the pluggable renderer system."""

import json

import click
import typer

from typer_manifest import (
    CompactMarkdownRenderer,
    JsonRenderer,
    MarkdownRenderer,
    Renderer,
    collect_manifest,
    render_manifest,
)


def test_collect_manifest_simple_click():
    """Test that collect_manifest works (replaces build_manifest)."""

    @click.command()
    def hello() -> None:
        """Say hello."""
        pass

    manifest = collect_manifest(hello, root_command_name="cli")
    assert manifest["name"] == "cli"
    assert len(manifest["commands"]) == 1
    assert manifest["commands"][0]["name"] == "cli"


def test_json_renderer_default():
    """Test JsonRenderer with default settings."""
    manifest = {"name": "test", "commands": []}
    renderer = JsonRenderer()
    output = renderer(manifest)

    # Should be valid JSON
    parsed = json.loads(output)
    assert parsed["name"] == "test"
    assert parsed["commands"] == []

    # Should have default indentation
    assert "\n" in output  # Multi-line with indentation


def test_json_renderer_custom_indent():
    """Test JsonRenderer with custom indentation."""
    manifest = {"name": "test", "commands": [{"name": "cmd"}]}
    renderer = JsonRenderer(indent=4)
    output = renderer(manifest)

    # Check indentation (4 spaces)
    lines = output.split("\n")
    assert any(line.startswith("    ") for line in lines)


def test_json_renderer_sorted_keys():
    """Test JsonRenderer with sorted keys."""
    manifest = {"zzzname": "test", "aaacommands": []}
    renderer = JsonRenderer(sort_keys=True)
    output = renderer(manifest)

    # Keys should be alphabetically sorted
    assert output.index("aaacommands") < output.index("zzzname")


def test_markdown_renderer():
    """Test MarkdownRenderer output format."""

    @click.group()
    def cli() -> None:
        """Test CLI."""
        pass

    @cli.command()
    def hello() -> None:
        """Say hello."""
        pass

    @cli.command()
    def goodbye() -> None:
        """Say goodbye."""
        pass

    manifest = collect_manifest(cli, root_command_name="myapp")
    renderer = MarkdownRenderer()
    output = renderer(manifest)

    assert "# myapp commands" in output
    assert "- myapp hello: Say hello." in output
    assert "- myapp goodbye: Say goodbye." in output


def test_markdown_renderer_nested():
    """Test MarkdownRenderer with nested commands."""

    @click.group()
    def cli() -> None:
        """Root."""
        pass

    @cli.group()
    def db() -> None:
        """Database commands."""
        pass

    @db.command()
    def migrate() -> None:
        """Run migrations."""
        pass

    manifest = collect_manifest(cli, root_command_name="app")
    renderer = MarkdownRenderer()
    output = renderer(manifest)

    assert "# app commands" in output
    assert "- app db: Database commands." in output
    assert "  - app db migrate: Run migrations." in output


def test_compact_markdown_renderer():
    """Test CompactMarkdownRenderer (no help text)."""

    @click.group()
    def cli() -> None:
        """Test CLI."""
        pass

    @cli.command()
    def hello() -> None:
        """Say hello."""
        pass

    manifest = collect_manifest(cli, root_command_name="myapp")
    renderer = CompactMarkdownRenderer()
    output = renderer(manifest)

    assert "# myapp commands" in output
    assert "- myapp hello" in output
    # Should NOT include help text
    assert "Say hello" not in output


def test_render_manifest_with_json_format():
    """Test render_manifest with format='json'."""
    manifest = {"name": "test", "commands": []}
    output = render_manifest(manifest, format="json")

    parsed = json.loads(output)
    assert parsed["name"] == "test"


def test_render_manifest_with_markdown_format():
    """Test render_manifest with format='markdown'."""
    manifest = {
        "name": "myapp",
        "commands": [{"name": "hello", "path": "myapp hello", "help": "Hi", "commands": []}],
    }
    output = render_manifest(manifest, format="markdown")

    assert "# myapp commands" in output
    assert "- myapp hello: Hi" in output


def test_render_manifest_with_compact_format():
    """Test render_manifest with format='compact'."""
    manifest = {
        "name": "myapp",
        "commands": [{"name": "hello", "path": "myapp hello", "help": "Hi", "commands": []}],
    }
    output = render_manifest(manifest, format="compact")

    assert "# myapp commands" in output
    assert "- myapp hello" in output
    assert "Hi" not in output  # No help text in compact mode


def test_render_manifest_with_custom_renderer_function():
    """Test render_manifest with a custom renderer function."""

    def my_renderer(manifest):
        return f"CLI: {manifest['name']}"

    manifest = {"name": "myapp", "commands": []}
    output = render_manifest(manifest, renderer=my_renderer)

    assert output == "CLI: myapp"


def test_render_manifest_with_custom_renderer_class():
    """Test render_manifest with a custom renderer class."""

    class MyRenderer:
        def __call__(self, manifest):
            return f"Application: {manifest['name']}"

    manifest = {"name": "myapp", "commands": []}
    output = render_manifest(manifest, renderer=MyRenderer())

    assert output == "Application: myapp"


def test_render_manifest_with_template():
    """Test render_manifest with a template string."""
    manifest = {"name": "myapp", "commands": []}
    template = "# My CLI\n\n{{ manifest }}"
    output = render_manifest(manifest, template=template)

    assert output.startswith("# My CLI\n\n")
    assert '"name": "myapp"' in output


def test_render_manifest_invalid_format():
    """Test render_manifest with invalid format raises ValueError."""
    manifest = {"name": "test", "commands": []}

    try:
        render_manifest(manifest, format="invalid")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Unknown format" in str(e)
        assert "invalid" in str(e)


def test_render_manifest_priority_renderer_over_template():
    """Test that custom renderer takes priority over template."""

    def my_renderer(manifest):
        return "Custom"

    manifest = {"name": "test", "commands": []}
    output = render_manifest(manifest, renderer=my_renderer, template="Template: {{ manifest }}")

    # Should use renderer, not template
    assert output == "Custom"


def test_render_manifest_priority_template_over_format():
    """Test that template takes priority over format."""
    manifest = {"name": "test", "commands": []}
    output = render_manifest(manifest, template="Custom", format="markdown")

    # Should use template, not format
    assert output == "Custom"


def test_renderer_protocol_with_function():
    """Test that a simple function implements the Renderer protocol."""

    def my_renderer(manifest):
        return str(manifest)

    # Should be recognized as a Renderer
    assert isinstance(my_renderer, Renderer)


def test_renderer_protocol_with_class():
    """Test that a class with __call__ implements the Renderer protocol."""

    class MyRenderer:
        def __call__(self, manifest):
            return "rendered"

    renderer = MyRenderer()
    assert isinstance(renderer, Renderer)


def test_collect_manifest_with_typer_app():
    """Test collect_manifest with Typer app (new API)."""
    app = typer.Typer()

    @app.command()
    def greet(name: str = typer.Option("World", "--name", help="Name to greet")) -> None:
        """Greet someone."""
        pass

    manifest = collect_manifest(app, root_command_name="myapp")
    assert manifest["name"] == "myapp"
    assert len(manifest["commands"]) == 1


def test_integration_collect_and_render():
    """Test full workflow: collect and render with different renderers."""
    app = typer.Typer()

    @app.command()
    def hello() -> None:
        """Say hello."""
        pass

    @app.command()
    def goodbye() -> None:
        """Say goodbye."""
        pass

    # Collect once
    manifest = collect_manifest(app, "myapp")

    # Render in multiple formats
    json_output = render_manifest(manifest, format="json")
    md_output = render_manifest(manifest, format="markdown")
    compact_output = render_manifest(manifest, format="compact")

    # All should work
    assert "myapp" in json_output
    assert "Say hello" in md_output
    assert "Say hello" not in compact_output
