"""Type definitions for typer-manifest."""

from typing import Any, Protocol, runtime_checkable

# Type alias for manifest structure
Manifest = dict[str, Any]


@runtime_checkable
class Renderer(Protocol):
    """Protocol for custom manifest renderers.

    Any callable that accepts a Manifest and returns a string can be used as a renderer.

    Example:
        >>> def my_renderer(manifest: Manifest) -> str:
        ...     return f"CLI: {manifest['name']}"
        >>> isinstance(my_renderer, Renderer)
        True
    """

    def __call__(self, manifest: Manifest) -> str:
        """Render a manifest to a string.

        Args:
            manifest: The manifest dictionary to render

        Returns:
            A string representation of the manifest
        """
        ...
