"""Utilities for buildthings unit tests.

Version Added:
    1.1
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
from contextlib import contextmanager
from importlib.metadata import Distribution
from typing import TYPE_CHECKING
from zipfile import ZipFile

from pyproject_hooks import BuildBackendHookCaller

import buildthings

if TYPE_CHECKING:
    from collections.abc import Iterator


_buildthings_path = os.path.dirname(buildthings.__file__)


@contextmanager
def setup_pyproject_toml(
    content: str,
) -> Iterator[None]:
    """Set up a temp working directory with a pyproject.toml file.

    This is a context manager that unit tests can use to establish a working
    package directory for testing. It will write the provided content to a
    :file:`pyproject.toml` in the directory and then run the test within it.
    The directory and all contents will be cleaned up after the test.

    Version Added:
        1.1

    Args:
        content (str):
            The content to write to the :file:`pyproject.toml` file.

    Context:
        The test will run within the populated temp directory.
    """
    prev_cwd = os.getcwd()
    dirpath = tempfile.mkdtemp()

    os.chdir(dirpath)

    with open('pyproject.toml', 'w', encoding='utf-8') as fp:
        fp.write("""
            [build-system]
            requires = ['buildthings']
            build-backend = 'buildthings.backend'

            [project]
            name = 'buildthings-test'
            version = '1.0'
        """)
        fp.write(content)

    try:
        yield
    finally:
        os.chdir(prev_cwd)
        shutil.rmtree(dirpath)


@contextmanager
def setup_backend(
    pyproject_toml: str,
) -> Iterator[BuildBackendHookCaller]:
    """Set up a backend environment and hook caller for a test.

    This will set up a tree with a :file:`pyproject.toml` and then configure
    a backend hook caller so that a hook can be invoked in a subprocess.

    Version Added:
        1.1

    Args:
        pyproject_toml (str):
            The content to write to the :file:`pyproject.toml` file.

    Context:
        pyproject_hooks.BuildBackendHookCaller:
        The test will run within the populated temp directory with a backend
        hook caller instance.
    """
    with setup_pyproject_toml(pyproject_toml):
        os.symlink(_buildthings_path, 'buildthings')

        yield BuildBackendHookCaller(
            source_dir=os.getcwd(),
            build_backend='buildthings.backend',
            backend_path='.',
            runner=None,
            python_executable=sys.executable,
        )


def get_dist_from_wheel(
    path: str,
) -> Distribution:
    """Return a Distribution from a wheel file.

    This assumes a specific name and version for the package.

    Version Added:
        1.1

    Args:
        path (str):
            The path to the wheel.

    Returns:
        importlib.metadata.Distribution:
        The resulting distribution.
    """
    with ZipFile(path) as zf:
        zf.extractall('.wheel')

    dist = Distribution.at('.wheel/buildthings_test-1.0.dist-info')
    assert dist.name

    return dist
