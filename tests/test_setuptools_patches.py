"""Tests for buildthings.setuptools_patches.

Version Added:
    1.1
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from setuptools.config.pyprojecttoml import _ConfigExpander

from buildthings import setuptools_patches
from buildthings.setuptools_patches import (
    _old_ConfigExpander_init,
    patch_setuptools,
    patch_setuptools_package_deps,
)

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Any


@pytest.fixture(autouse=True)
def patched_setuptools() -> Iterator[None]:
    """Apply the buildthings patch to _ConfigExpander.

    This will apply the patch for the duration of one test, then restore the
    original ``__init__`` and clear any registered post-funcs.

    ``patch_setuptools()`` asserts it hasn't been called before, so we restore
    ``_ConfigExpander.__init__`` to the original between tests.

    Version Added:
        1.1
    """
    saved_init = _ConfigExpander.__init__
    _ConfigExpander.__init__ = _old_ConfigExpander_init
    setuptools_patches._config_expander_post_funcs.clear()

    patch_setuptools()

    try:
        yield
    finally:
        _ConfigExpander.__init__ = saved_init
        setuptools_patches._config_expander_post_funcs.clear()


def _make_pyproject_config(
    deps_dynamic: bool = True,
) -> dict[str, Any]:
    """Return a minimal pyproject.toml-style config for _ConfigExpander.

    The "dependencies" field is marked dynamic by default, mirroring how
    djblets and Review Board's pyproject.toml files declare dependencies that
    buildthings then injects.

    Version Added:
        1.1

    Args:
        deps_dynamic (bool, optional):
            Whether to include dynamic dependencies.

    Returns:
        dict:
        The config to use for the test.
    """
    project: dict[str, Any] = {
        'name': 'example',
    }

    if deps_dynamic:
        project['dynamic'] = ['dependencies']

    return {'project': project}


def test_patch_applies_deps_to_next_expander() -> None:
    """Test that patch is applied to the next _ConfigExpander.

    Version Added:
        1.1
    """
    patch_setuptools_package_deps(['foo>=1', 'bar'])

    expander = _ConfigExpander(_make_pyproject_config())

    assert expander.project_cfg['dependencies'] == ['foo>=1', 'bar']
    assert 'dependencies' not in expander.dynamic


def test_patch_after_prior_expander_does_not_assert() -> None:
    """Test patching after a prior expander has run.

    An expander built before any patch is registered must not poison the
    next ``patch_setuptools_package_deps()`` call.

    :py:mod:`pyproject_api` keeps a single worker process across all PEP 517
    hooks. The earlier ``get_requires_for_build_*`` hooks construct a
    ``Distribution`` (and therefore a ``_ConfigExpander``) before
    ``prepare_metadata_for_build_wheel`` ever calls
    ``patch_setuptools_package_deps()``. The patch call must not raise
    just because some unrelated expander was instantiated earlier.

    Version Added:
        1.1
    """
    # Simulate the earlier hook -- a _ConfigExpander is built before any
    # patch is registered.
    _ConfigExpander(_make_pyproject_config())

    # Now the later hook registers its deps. This must not raise.
    patch_setuptools_package_deps(['foo>=1'])

    # And the next expander -- the one we actually care about -- picks up
    # the deps.
    expander = _ConfigExpander(_make_pyproject_config())

    assert expander.project_cfg['dependencies'] == ['foo>=1']


def test_repeated_patch_calls_do_not_stack() -> None:
    """Test that repeated calls do not stack.

    Calling ``patch_setuptools_package_deps()`` twice replaces the patch rather
    than stacking it.

    Without replacement, both _patch_deps closures would run against the
    next expander, and ``project_cfg.setdefault('dependencies', []).extend()``
    would produce a duplicated dependency list.
    """
    patch_setuptools_package_deps(['foo>=1'])
    patch_setuptools_package_deps(['bar>=2'])

    expander = _ConfigExpander(_make_pyproject_config())

    assert expander.project_cfg['dependencies'] == ['bar>=2']
