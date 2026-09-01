# Copyright 2024 Christian Prior-Mamulyan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
