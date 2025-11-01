"""Collection logic for introspecting Typer/Click applications."""

from __future__ import annotations

from typing import Any

import click

from .types import Manifest

try:  # pragma: no cover - Typer optional
    from typer import Typer
    from typer.main import get_command as typer_get_command
except ImportError:  # pragma: no cover
    Typer = None  # type: ignore[misc, assignment]
    typer_get_command = None  # type: ignore[misc, assignment]


def _as_click_command(app: Any) -> click.Command:
    """Convert a Typer app or Click command to a Click Command object.

    Args:
        app: A Typer app or Click command object

    Returns:
        The underlying Click command

    Raises:
        TypeError: If the app is neither a Click command nor a Typer app
    """
    if isinstance(app, click.Command):
        return app
    if Typer is not None and isinstance(app, Typer):
        # Use typer.main.get_command to get the Click command without invoking the app
        if typer_get_command is not None:
            return typer_get_command(app)  # type: ignore[misc]
        # Fallback for older typer versions
        return app()  # type: ignore[operator]
    raise TypeError("Unsupported CLI application type; expected Click command or Typer app.")


def _serialize_command(command: click.Command, path: list[str]) -> dict[str, Any]:
    """Recursively serialize a Click command and its subcommands.

    Args:
        command: The Click command to serialize
        path: The command path from root (e.g., ['myapp', 'subcommand'])

    Returns:
        A dictionary containing the command's metadata, parameters, and subcommands
    """
    entry: dict[str, Any] = {
        "name": path[-1],
        "path": " ".join(path),
        "help": (command.help or "").strip(),
        "params": [],
        "commands": [],
    }

    for param in command.params:
        entry["params"].append(
            {
                "name": param.name,
                "opts": list(getattr(param, "opts", []) or []),
                "help": (getattr(param, "help", "") or "").strip(),
                "required": getattr(param, "required", False),
                "default": getattr(param, "default", None),
                "type": param.param_type_name,
            }
        )

    if isinstance(command, (click.MultiCommand, click.Group)):
        ctx = click.Context(command)
        sub_commands = command.list_commands(ctx) or []
        for sub_name in sub_commands:
            sub_cmd = command.get_command(ctx, sub_name)
            if sub_cmd is None:
                continue
            entry["commands"].append(_serialize_command(sub_cmd, path + [sub_name]))

    return entry


def collect_manifest(app: Any, root_command_name: str | None = None) -> Manifest:
    """Introspect a Click or Typer app and return a structured manifest.

    This function walks through the entire command structure of a Typer or Click
    application and returns a pure data structure (dictionary) representing all
    commands, subcommands, and their parameters.

    Args:
        app: A Typer app or Click command object
        root_command_name: Optional name for the root command. If not provided,
            attempts to derive from the command's name attribute, falling back to 'cli'

    Returns:
        A dictionary containing the complete command hierarchy with metadata

    Example:
        >>> from typer import Typer
        >>> app = Typer()
        >>> @app.command()
        ... def hello(name: str):
        ...     '''Say hello to someone'''
        ...     pass
        >>> manifest = collect_manifest(app, "myapp")
        >>> manifest['name']
        'myapp'
        >>> len(manifest['commands'])
        1
    """
    click_command = _as_click_command(app)
    root_name = (
        root_command_name
        or getattr(click_command, "name", None)
        or getattr(app, "name", "cli")
    )

    manifest: Manifest = {"name": root_name, "commands": []}

    if isinstance(click_command, (click.MultiCommand, click.Group)):
        ctx = click.Context(click_command)
        for name in click_command.list_commands(ctx) or []:
            sub = click_command.get_command(ctx, name)
            if sub is None:
                continue
            manifest["commands"].append(_serialize_command(sub, [root_name, name]))
    else:
        manifest["commands"].append(_serialize_command(click_command, [root_name]))

    return manifest
