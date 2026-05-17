"""Tests for buildthings.config.Config.

Version Added:
    1.1
"""

from __future__ import annotations

import pytest

from buildthings.config import PyProjectConfig
from buildthings.tests.utils import setup_pyproject_toml


def test_load_dependencies() -> None:
    """Test PyProjectConfig.load with dependencies.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'ReviewBoard>=8.0',
            'buildthings',
            'kgb~=7.0',
        ]
    """

    with setup_pyproject_toml(pyproject_toml):
        config = PyProjectConfig.from_file('pyproject.toml')

    assert config.package_dependencies == {
        'editable': {
            'dependencies': [
                'ReviewBoard>=8.0',
                'buildthings',
                'kgb~=7.0',
            ],
            'exclude_deps': [],
        },
        'sdist': {
            'dependencies': [
                'ReviewBoard>=8.0',
                'buildthings',
                'kgb~=7.0',
            ],
            'exclude_deps': [],
        },
        'wheel': {
            'dependencies': [
                'ReviewBoard>=8.0',
                'buildthings',
                'kgb~=7.0',
            ],
            'exclude_deps': [],
        },
    }


def test_load_dependencies_with_build_type_overrides() -> None:
    """Test PyProjectConfig.load with dependencies/exclude-deps with
    build type overrides.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'ReviewBoard>=8.0',
            'buildthings',
            'kgb~=7.0',
        ]

        [tool.buildthings.editable]
        dependencies = ['my-editable-dep']
        exclude-deps = ['exclude-editable-dep']

        [tool.buildthings.sdist]
        dependencies = ['my-sdist-dep']
        exclude-deps = ['exclude-sdist-dep']

        [tool.buildthings.wheel]
        dependencies = ['my-wheel-dep']
        exclude-deps = ['exclude-wheel-dep']
    """

    with setup_pyproject_toml(pyproject_toml):
        config = PyProjectConfig.from_file('pyproject.toml')

    assert config.package_dependencies == {
        'editable': {
            'dependencies': ['my-editable-dep'],
            'exclude_deps': ['exclude-editable-dep'],
        },
        'sdist': {
            'dependencies': ['my-sdist-dep'],
            'exclude_deps': ['exclude-sdist-dep'],
        },
        'wheel': {
            'dependencies': ['my-wheel-dep'],
            'exclude_deps': ['exclude-wheel-dep'],
        },
    }


def test_load_dependencies_with_non_list() -> None:
    """Test PyProjectConfig.load with dependencies with non-list.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = 'XXX'
    """

    with setup_pyproject_toml(pyproject_toml):
        with pytest.raises(ValueError) as excinfo:
            PyProjectConfig.from_file('pyproject.toml')

    assert str(excinfo.value) == (
        'Key "tool.buildthings.dependencies" must resolve to a list of '
        'dependencies (not \'XXX\'). Did you forget to list this in '
        '"tool.buildthings.dynamic"?'
    )


def test_load_dependencies_override_with_non_list() -> None:
    """Test PyProjectConfig.load with dependencies override with non-list.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings.editable]
        dependencies = 'XXX'
    """

    with setup_pyproject_toml(pyproject_toml):
        with pytest.raises(ValueError) as excinfo:
            config = PyProjectConfig.from_file('pyproject.toml')

            print(config.package_dependencies)

    assert str(excinfo.value) == (
        'Key "tool.buildthings.editable.dependencies" must resolve to a '
        'list (not str).'
    )
