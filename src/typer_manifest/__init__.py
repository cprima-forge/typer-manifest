"""Typer Manifest - Introspect Typer apps and export their command structure.

This package provides a pluggable system for collecting CLI structure information
and rendering it in various formats.

New API (recommended):
    - collect_manifest: Introspect CLI apps and return manifest dict
    - render_manifest: Render manifest with pluggable renderers
    - JsonRenderer, MarkdownRenderer, CompactMarkdownRenderer: Built-in renderers
    - Renderer: Protocol for custom renderers

Legacy API (backward compatibility):
    - build_manifest: Alias for collect_manifest
    - write_manifest: Collect and write as JSON file
    - render_manifest_list: Render as Markdown (delegates to MarkdownRenderer)
"""

# New modular API
from .collector import collect_manifest
from .renderers import (
    CompactMarkdownRenderer,
    JsonRenderer,
    MarkdownRenderer,
    render_manifest,
)
from .types import Manifest, Renderer

# Legacy API for backward compatibility
from .core import build_manifest, render_manifest_list, write_manifest

__version__ = "0.2.0"

__all__ = (
    # New API (recommended)
    "collect_manifest",
    "render_manifest",
    "JsonRenderer",
    "MarkdownRenderer",
    "CompactMarkdownRenderer",
    "Manifest",
    "Renderer",
    # Legacy API (maintained for compatibility)
    "build_manifest",
    "write_manifest",
    "render_manifest_list",
)
