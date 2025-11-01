"""Tests for typer_manifest package."""

import json
import tempfile
from pathlib import Path

import click
import typer

from typer_manifest import build_manifest, render_manifest_list, write_manifest


def test_build_manifest_simple_click_command() -> None:
    """Test building a manifest from a simple Click command."""

    @click.command()
    def hello() -> None:
        """Say hello."""
        pass

    manifest = build_manifest(hello, root_command_name="cli")
    assert manifest["name"] == "cli"
    assert len(manifest["commands"]) == 1

    cmd = manifest["commands"][0]
    assert cmd["name"] == "cli"
    assert cmd["path"] == "cli"
    assert cmd["help"] == "Say hello."
    assert cmd["params"] == []
    assert cmd["commands"] == []


def test_build_manifest_click_group() -> None:
    """Test building a manifest from a Click group with subcommands."""

    @click.group()
    def cli() -> None:
        """Root CLI."""
        pass

    @cli.command()
    def hello() -> None:
        """Say hello."""
        pass

    @cli.command()
    def goodbye() -> None:
        """Say goodbye."""
        pass

    manifest = build_manifest(cli, root_command_name="cli")
    assert manifest["name"] == "cli"
    assert len(manifest["commands"]) == 2

    # Commands may be in any order, so find them by name
    commands_by_name = {cmd["name"]: cmd for cmd in manifest["commands"]}

    hello_cmd = commands_by_name["hello"]
    assert hello_cmd["path"] == "cli hello"
    assert hello_cmd["help"] == "Say hello."

    goodbye_cmd = commands_by_name["goodbye"]
    assert goodbye_cmd["path"] == "cli goodbye"
    assert goodbye_cmd["help"] == "Say goodbye."


def test_build_manifest_typer_app() -> None:
    """Test building a manifest from a Typer app with a single command."""
    app = typer.Typer()

    @app.command()
    def greet(name: str = typer.Option("World", "--name", help="Name to greet")) -> None:
        """Greet someone."""
        pass

    # For single-command Typer apps, get_command() returns the command directly
    # So the manifest will contain just that command with the root name
    manifest = build_manifest(app, root_command_name="myapp")
    assert manifest["name"] == "myapp"
    assert len(manifest["commands"]) == 1

    # The command gets the root name since it's a single command app
    greet_cmd = manifest["commands"][0]
    assert greet_cmd["name"] == "myapp"
    assert greet_cmd["path"] == "myapp"
    assert greet_cmd["help"] == "Greet someone."
    assert len(greet_cmd["params"]) >= 1  # May include help option

    # Find the name parameter
    name_param = next((p for p in greet_cmd["params"] if p["name"] == "name"), None)
    assert name_param is not None
    assert "--name" in name_param["opts"]
    assert name_param["help"] == "Name to greet"
    assert name_param["default"] == "World"


def test_build_manifest_nested_groups() -> None:
    """Test building a manifest with nested command groups."""

    @click.group()
    def cli() -> None:
        """Root CLI."""
        pass

    @cli.group()
    def db() -> None:
        """Database commands."""
        pass

    @db.command()
    def migrate() -> None:
        """Run migrations."""
        pass

    @db.command()
    def seed() -> None:
        """Seed database."""
        pass

    manifest = build_manifest(cli, root_command_name="app")
    assert manifest["name"] == "app"
    assert len(manifest["commands"]) == 1

    db_cmd = manifest["commands"][0]
    assert db_cmd["name"] == "db"
    assert db_cmd["path"] == "app db"
    assert db_cmd["help"] == "Database commands."
    assert len(db_cmd["commands"]) == 2

    migrate_cmd = db_cmd["commands"][0]
    assert migrate_cmd["name"] == "migrate"
    assert migrate_cmd["path"] == "app db migrate"
    assert migrate_cmd["help"] == "Run migrations."


def test_build_manifest_with_parameters() -> None:
    """Test that command parameters are captured correctly."""

    @click.command()
    @click.option("--verbose", "-v", is_flag=True, help="Verbose output")
    @click.option("--count", "-c", default=1, help="Number of times")
    @click.argument("name")
    def greet(name: str, verbose: bool, count: int) -> None:
        """Greet someone."""
        pass

    manifest = build_manifest(greet, root_command_name="cli")
    cmd = manifest["commands"][0]
    assert len(cmd["params"]) == 3

    # Check verbose option
    verbose_param = next(p for p in cmd["params"] if p["name"] == "verbose")
    assert "--verbose" in verbose_param["opts"]
    assert "-v" in verbose_param["opts"]
    assert verbose_param["help"] == "Verbose output"
    # Click reports boolean flags as "option" type, not "flag"
    assert verbose_param["type"] == "option"

    # Check count option
    count_param = next(p for p in cmd["params"] if p["name"] == "count")
    assert count_param["default"] == 1
    assert count_param["help"] == "Number of times"

    # Check name argument
    name_param = next(p for p in cmd["params"] if p["name"] == "name")
    assert name_param["type"] == "argument"
    assert name_param["required"] is True


def test_write_manifest() -> None:
    """Test writing a manifest to a JSON file."""

    @click.group()
    def cli() -> None:
        """Test CLI."""
        pass

    @cli.command()
    def test() -> None:
        """Test command."""
        pass

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        temp_path = f.name

    try:
        write_manifest(cli, temp_path, root_command_name="testcli")

        # Read and verify the file
        content = Path(temp_path).read_text(encoding="utf-8")
        data = json.loads(content)

        assert data["name"] == "testcli"
        assert len(data["commands"]) == 1
        assert data["commands"][0]["name"] == "test"
    finally:
        Path(temp_path).unlink()


def test_render_manifest_list() -> None:
    """Test rendering a manifest as a Markdown list."""

    @click.group()
    def cli() -> None:
        """Root CLI."""
        pass

    @cli.command()
    def hello() -> None:
        """Say hello."""
        pass

    @cli.command()
    def goodbye() -> None:
        """Say goodbye."""
        pass

    manifest = build_manifest(cli, root_command_name="myapp")
    output = render_manifest_list(manifest)

    assert "# myapp commands" in output
    assert "- myapp hello: Say hello." in output
    assert "- myapp goodbye: Say goodbye." in output


def test_render_manifest_list_nested() -> None:
    """Test rendering a nested manifest structure."""

    @click.group()
    def cli() -> None:
        """Root CLI."""
        pass

    @cli.group()
    def db() -> None:
        """Database commands."""
        pass

    @db.command()
    def migrate() -> None:
        """Run migrations."""
        pass

    manifest = build_manifest(cli, root_command_name="app")
    output = render_manifest_list(manifest)

    assert "# app commands" in output
    assert "- app db: Database commands." in output
    assert "  - app db migrate: Run migrations." in output


def test_build_manifest_no_help_text() -> None:
    """Test handling commands without help text."""

    @click.command()
    def nohelp() -> None:
        pass

    manifest = build_manifest(nohelp, root_command_name="cli")
    cmd = manifest["commands"][0]
    assert cmd["help"] == ""


def test_typer_app_with_multiple_commands() -> None:
    """Test a Typer app with multiple commands and various parameter types."""
    app = typer.Typer()

    @app.command()
    def init(force: bool = typer.Option(False, "--force", "-f", help="Force init")) -> None:
        """Initialize the project."""
        pass

    @app.command()
    def build(
        output: str = typer.Option("dist", "--output", "-o", help="Output directory"),
        verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode"),
    ) -> None:
        """Build the project."""
        pass

    manifest = build_manifest(app, root_command_name="proj")
    assert manifest["name"] == "proj"
    assert len(manifest["commands"]) == 2

    init_cmd = next(cmd for cmd in manifest["commands"] if cmd["name"] == "init")
    assert init_cmd["path"] == "proj init"
    assert init_cmd["help"] == "Initialize the project."
    # Find force parameter (may have help option too)
    force_param = next((p for p in init_cmd["params"] if p["name"] == "force"), None)
    assert force_param is not None
    assert "--force" in force_param["opts"]

    build_cmd = next(cmd for cmd in manifest["commands"] if cmd["name"] == "build")
    assert build_cmd["path"] == "proj build"
    # Check for output and verbose parameters
    output_param = next((p for p in build_cmd["params"] if p["name"] == "output"), None)
    assert output_param is not None
    verbose_param = next((p for p in build_cmd["params"] if p["name"] == "verbose"), None)
    assert verbose_param is not None
