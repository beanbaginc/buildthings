"""Tests for buildthings.local_paths.

Version Added:
    1.2
"""

from __future__ import annotations

import os
import tempfile

from buildthings.local_paths import (get_local_dep_paths,
                                     get_local_dep_paths_for_tree)
from buildthings.tests.utils import setup_pyproject_toml


def test_get_local_dep_paths() -> None:
    """Testing get_local_dep_paths.

    Version Added:
        1.2
    """
    temp_path1 = tempfile.mkdtemp()
    temp_path2 = tempfile.mkdtemp()

    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'ReviewBoard>=8.0',
            'buildthings',
            'kgb~=7.0',
        ]
    """

    try:
        with setup_pyproject_toml(pyproject_toml):
            local_packages_path = os.path.join(os.getcwd(), '.local-packages')

            os.mkdir(local_packages_path, 0o755)
            os.symlink(temp_path1, os.path.join(local_packages_path, 'dep1'))
            os.symlink(temp_path2, os.path.join(local_packages_path, 'dep2'))

            assert get_local_dep_paths(local_packages_path) == {
                'dep1': temp_path1,
                'dep2': temp_path2,
            }
    finally:
        os.rmdir(temp_path1)
        os.rmdir(temp_path2)


def test_get_local_dep_paths_for_tree() -> None:
    """Testing get_local_dep_paths_for_tree.

    Version Added:
        1.2
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'ReviewBoard>=8.0',
            'buildthings',
            'kgb~=7.0',
        ]
    """

    broken_pyproject_toml = """
        [tool.buildthings]
        dependencies[
    """

    with setup_pyproject_toml(pyproject_toml) as main_path, \
         setup_pyproject_toml(pyproject_toml) as dep_1, \
         setup_pyproject_toml(pyproject_toml) as dep_2, \
         setup_pyproject_toml(pyproject_toml) as dep_3, \
         setup_pyproject_toml(broken_pyproject_toml) as dep_4, \
         setup_pyproject_toml(pyproject_toml) as dep_5:
        # Set up the main package -> dep1, dep2.
        local_packages = os.path.join(main_path, '.local-packages')
        os.mkdir(local_packages, 0o755)
        os.symlink(dep_1, os.path.join(local_packages, 'dep1'))
        os.symlink(dep_2, os.path.join(local_packages, 'dep2'))

        # Set up dep1 -> dep2, dep3.
        local_packages = os.path.join(dep_1, '.local-packages')
        os.mkdir(local_packages, 0o755)
        os.symlink(dep_2, os.path.join(local_packages, 'dep2'))
        os.symlink(dep_3, os.path.join(local_packages, 'dep3'))

        # Set up dep3 -> dep1, dep4.
        local_packages = os.path.join(dep_3, '.local-packages')
        os.mkdir(local_packages, 0o755)
        os.symlink(dep_1, os.path.join(local_packages, 'dep1'))
        os.symlink(dep_4, os.path.join(local_packages, 'dep4'))

        # Set up dep4 -> dep5.
        local_packages = os.path.join(dep_4, '.local-packages')
        os.mkdir(local_packages, 0o755)
        os.symlink(dep_5, os.path.join(local_packages, 'dep5'))

        result = get_local_dep_paths_for_tree(
            os.path.join(main_path, '.local-packages'))

        assert result == {
            'dep1': dep_1,
            'dep2': dep_2,
            'dep3': dep_3,
            'dep4': dep_4,
        }
