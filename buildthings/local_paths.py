"""Utilities for applying .local-packages paths to dependency lists.

Version Added:
    1.0
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


#: A cache of computed local paths for dependencies.
#:
#: This will only be around for the duration of the build backend hook
#: invocation. Build frontends are expected to invoke each independent hook
#: in its own subprocess. This means this does not need to worry about
#: caching for each build type.
#:
#: Version Added:
#:     1.0
_local_dep_paths: (Mapping[str, str] | None) = None


def get_local_dep_paths(
    local_packages_path: str,
) -> Mapping[str, str]:
    """Return a mapping of dependencies to local paths.

    Args:
        local_packages_path (str):
            The path to the :file:`.local-packages` directory.

    Returns:
        dict:
        A mapping of normalized dependency name to path.
    """
    global _local_dep_paths

    if _local_dep_paths is None:
        local_paths: dict[str, str] = {}

        if local_packages_path and os.path.exists(local_packages_path):
            for name in os.listdir(local_packages_path):
                local_paths[canonicalize_name(name)] = os.path.abspath(
                    os.readlink(os.path.join(local_packages_path, name)))

        _local_dep_paths = local_paths

    return _local_dep_paths


def apply_local_dep_paths(
    *,
    local_packages_path: str | None,
    deps: Sequence[str],
) -> Sequence[str]:
    """Apply local file paths to a list of dependencies.

    This will compare a list of dependencies to any symlinks in
    :file:`.local-packages`, using canonicalized package names.

    If any are found, the dependency will be replaced with::

        <package> @ file://<path>

    Version Added:
        1.0

    Args:
        local_packages_path (str):
            The path to the :file:`.local-packages` directory.

            If ``None``, local dependencies won't be applied.

        deps (list of str):
            The list of dependencies to process.

    Returns:
        list of str:
        The resulting list of dependencies.
    """
    if (deps and
        local_packages_path and
        (local_paths := get_local_dep_paths(local_packages_path))):
        # If any of the dependencies are overridden by a local development
        # package, replace it with that path.
        new_deps: list[str] = []

        for dep in deps:
            req = Requirement(dep)
            dep_name = canonicalize_name(req.name)

            try:
                package_path = local_paths[dep_name]
            except KeyError:
                new_deps.append(dep)
                continue

            new_deps.append(f'{dep_name} @ file://{package_path}')

        deps = new_deps

    return deps
