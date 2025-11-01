"""Built-in renderers and rendering utilities for typer-manifest."""

from __future__ import annotations

import json
from typing import Any

from .types import Manifest, Renderer


class JsonRenderer:
    """Renders a manifest as formatted JSON.

    Args:
        indent: Number of spaces for indentation (default: 2)
        sort_keys: Whether to sort dictionary keys (default: False)

    Example:
        >>> renderer = JsonRenderer(indent=4)
        >>> manifest = {"name": "myapp", "commands": []}
        >>> output = renderer(manifest)
        >>> '"name": "myapp"' in output
        True
    """

    def __init__(self, indent: int = 2, sort_keys: bool = False):
        """Initialize the JSON renderer.

        Args:
            indent: Number of spaces for indentation
            sort_keys: Whether to sort dictionary keys alphabetically
        """
        self.indent = indent
        self.sort_keys = sort_keys

    def __call__(self, manifest: Manifest) -> str:
        """Render manifest as JSON.

        Args:
            manifest: The manifest to render

        Returns:
            JSON-formatted string
        """
        return json.dumps(manifest, indent=self.indent, sort_keys=self.sort_keys)


class MarkdownRenderer:
    """Renders a manifest as a hierarchical Markdown bullet list with help text.

    Example:
        >>> renderer = MarkdownRenderer()
        >>> manifest = {
        ...     "name": "myapp",
        ...     "commands": [{
        ...         "name": "hello",
        ...         "path": "myapp hello",
        ...         "help": "Say hello",
        ...         "params": [],
        ...         "commands": []
        ...     }]
        ... }
        >>> output = renderer(manifest)
        >>> "# myapp commands" in output
        True
        >>> "- myapp hello: Say hello" in output
        True
    """

    def __call__(self, manifest: Manifest) -> str:
        """Render manifest as Markdown.

        Args:
            manifest: The manifest to render

        Returns:
            Markdown-formatted string with hierarchical bullet list
        """
        lines: list[str] = [f"# {manifest.get('name', 'cli')} commands"]

        def walk(commands: list[dict[str, Any]], depth: int = 0) -> None:
            indent = "  " * depth
            for cmd in commands:
                line = f"{indent}- {cmd.get('path', cmd.get('name', 'command'))}"
                help_text = cmd.get("help")
                if help_text:
                    line += f": {help_text}"
                lines.append(line)
                if cmd.get("commands"):
                    walk(cmd["commands"], depth + 1)

        walk(manifest.get("commands", []))
        return "\n".join(lines)


class CompactMarkdownRenderer:
    """Renders a manifest as a compact Markdown list without help text.

    Example:
        >>> renderer = CompactMarkdownRenderer()
        >>> manifest = {
        ...     "name": "myapp",
        ...     "commands": [{
        ...         "name": "hello",
        ...         "path": "myapp hello",
        ...         "help": "Say hello",
        ...         "params": [],
        ...         "commands": []
        ...     }]
        ... }
        >>> output = renderer(manifest)
        >>> "# myapp commands" in output
        True
        >>> "- myapp hello" in output
        True
        >>> "Say hello" not in output
        True
    """

    def __call__(self, manifest: Manifest) -> str:
        """Render manifest as compact Markdown.

        Args:
            manifest: The manifest to render

        Returns:
            Markdown-formatted string with command paths only
        """
        lines: list[str] = [f"# {manifest.get('name', 'cli')} commands"]

        def walk(commands: list[dict[str, Any]], depth: int = 0) -> None:
            indent = "  " * depth
            for cmd in commands:
                path = cmd.get("path", cmd.get("name", "command"))
                lines.append(f"{indent}- {path}")
                if cmd.get("commands"):
                    walk(cmd["commands"], depth + 1)

        walk(manifest.get("commands", []))
        return "\n".join(lines)


def render_manifest(
    manifest: Manifest,
    *,
    renderer: Renderer | None = None,
    template: str | None = None,
    format: str = "json",
) -> str:
    """Render a manifest using a pluggable renderer system.

    This function provides multiple ways to render a manifest:
    1. Custom renderer (callable/class)
    2. Simple template string substitution
    3. Built-in format renderers

    Args:
        manifest: The manifest dictionary to render
        renderer: Optional custom renderer (callable or Renderer instance)
        template: Optional template string with {{ manifest }} placeholder
        format: Built-in format to use if no renderer/template specified.
            Options: "json" (default), "markdown", "compact"

    Returns:
        Rendered manifest as a string

    Raises:
        ValueError: If an unknown format is specified

    Examples:
        >>> manifest = {"name": "myapp", "commands": []}

        >>> # Using built-in format
        >>> output = render_manifest(manifest, format="json")
        >>> isinstance(output, str)
        True

        >>> # Using custom renderer function
        >>> def my_renderer(m):
        ...     return f"CLI: {m['name']}"
        >>> render_manifest(manifest, renderer=my_renderer)
        'CLI: myapp'

        >>> # Using template
        >>> render_manifest(manifest, template="Name: {{ manifest }}")
        'Name: {...}'

        >>> # Using custom renderer class
        >>> class MyRenderer:
        ...     def __call__(self, m):
        ...         return f"App: {m['name']}"
        >>> render_manifest(manifest, renderer=MyRenderer())
        'App: myapp'
    """
    # Priority 1: Custom renderer
    if renderer is not None:
        return renderer(manifest)

    # Priority 2: Template string
    if template is not None:
        manifest_json = json.dumps(manifest, indent=2)
        return template.replace("{{ manifest }}", manifest_json)

    # Priority 3: Built-in format renderers
    if format == "json":
        return JsonRenderer()(manifest)
    elif format == "markdown":
        return MarkdownRenderer()(manifest)
    elif format == "compact":
        return CompactMarkdownRenderer()(manifest)
    else:
        raise ValueError(
            f"Unknown format: {format!r}. "
            f"Valid options are: 'json', 'markdown', 'compact'"
        )
