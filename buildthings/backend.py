"""Build backend for buildthings.

Version Added:
    1.0
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from typing import TYPE_CHECKING

from setuptools import build_meta as _build_meta
from typing_extensions import TypeAlias

from buildthings.config import IsolationConfig, PyProjectConfig
from buildthings.local_paths import apply_local_dep_paths

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from buildthings.config import BuildStep, BuildType

    ConfigSettings: TypeAlias = Mapping[
        str,
        str | list[str] | None,
    ]


# Inject all default hooks from setuptools as defaults into this module.
from setuptools.build_meta import *  # noqa


logger = logging.getLogger(__name__)


#: A cached instance of the loaded pyproject.toml state.
#:
#: Version Added:
#:     1.0
_config: (PyProjectConfig | None) = None


def get_requires_for_build_editable(
    config_settings: (ConfigSettings | None) = None,
) -> Sequence[str]:
    """Return build-time requirements for editable builds.

    This will return the standard dependencies for building the editable
    install by default.

    Additional dependencies can be provided or modified by:

    .. code-block:: toml

       [tool.buildthings.isolation.editable]
       include-dev-deps = true
       include-install-deps = true
       exclude-deps = ['somedep']

    If any of the resulting dependencies are overriden by local dependencies
    found in :file:`.local-packages/`, then the local package paths will
    take precedence.

    Version Added:
        1.0

    Args:
        config_settings (dict, optional):
            Configuration settings to pass to the build backend.

    Returns:
        list of str:
        The list of build-time dependencies.
    """
    return _get_requires_for_build(
        build_type='editable',
        config_settings=config_settings,
    )


def get_requires_for_build_sdist(
    config_settings: (ConfigSettings | None) = None,
) -> Sequence[str]:
    """Return build-time requirements for source distributions.

    This will return the standard dependencies for building the source
    distribution by default.

    Additional dependencies can be provided or modified by:

    .. code-block:: toml

       [tool.buildthings.isolation.sdist]
       include-dev-deps = true
       include-install-deps = true
       exclude-deps = ['somedep']

    If any of the resulting dependencies are overriden by local dependencies
    found in :file:`.local-packages/`, then the local package paths will
    take precedence.

    Version Added:
        1.0

    Args:
        config_settings (dict, optional):
            Configuration settings to pass to Setuptools.

    Returns:
        list of str:
        The list of build-time dependencies.
    """
    return _get_requires_for_build(
        build_type='sdist',
        config_settings=config_settings,
    )


def get_requires_for_build_wheel(
    config_settings: (ConfigSettings | None) = None,
) -> Sequence[str]:
    """Return build-time requirements for wheel distributions.

    This will return the standard dependencies for building the wheel by
    default.

    Additional dependencies can be provided or modified by:

    .. code-block:: toml

       [tool.buildthings.isolation.wheel]
       include-dev-deps = true
       include-install-deps = true
       exclude-deps = ['somedep']

    If any of the resulting dependencies are overriden by local dependencies
    found in :file:`.local-packages/`, then the local package paths will
    take precedence.

    Version Added:
        1.0

    Args:
        config_settings (dict, optional):
            Configuration settings to pass to Setuptools.

    Returns:
        list of str:
        The list of build-time dependencies.
    """
    return _get_requires_for_build(
        build_type='wheel',
        config_settings=config_settings,
    )


def prepare_metadata_for_build_editable(
    metadata_directory: str,
    config_settings: (ConfigSettings | None) = None,
) -> str:
    """Prepare metadata for an editable build.

    This will write out the package's editable dependencies to a temporary
    file so that :file:`pyproject.toml` can reference it.

    Version Added:
        1.0

    Args:
        metadata_directory (str):
            The target directory for metadata.

        config_settings (dict, optional):
            Configuration settings to pass to Setuptools.

    Returns:
        str:
        The basename for the generated ``.dist-info`` directory.
    """
    _write_dependencies(_get_editable_package_dependencies())

    return _build_meta.prepare_metadata_for_build_editable(
        metadata_directory,
        config_settings,
    )


def prepare_metadata_for_build_wheel(
    metadata_directory: str,
    config_settings: (ConfigSettings | None) = None,
) -> str:
    """Prepare metadata for a wheel distribution.

    This will write out the package's dependencies to a temporary file
    so that :file:`pyproject.toml` can reference it.

    Version Added:
        1.0

    Args:
        metadata_directory (str):
            The target directory for metadata.

        config_settings (dict, optional):
            Configuration settings to pass to Setuptools.

    Returns:
        str:
        The basename for the generated ``.dist-info`` directory.
    """
    config = _get_config()

    _write_dependencies(config.dependencies)

    return _build_meta.prepare_metadata_for_build_wheel(
        metadata_directory,
        config_settings,
    )


def build_editable(
    wheel_directory: str,
    config_settings: (ConfigSettings | None) = None,
    metadata_directory: (str | None) = None,
) -> str:
    """Build an editable environment.

    This will perform the following steps:

    1. Write out the editable dependencies to a file for setuptools to load.
    2. If configured, set up the NPM workspaces and install NPM packages.
    3. Run any package-defined build steps for editable mode.
    4. Build the editable install in compat mode (which allows for static
       instead of dynamic lookup of packages, needed for type checkers
       and similar tools).

    Version Added:
        1.0

    Args:
        wheel_directory (str):
            The directory in which to place the editable wheel.

        config_settings (dict, optional):
            Any configuration settings to apply for the build.

        metadata_directory (str, optional):
            A custom path to the ``.dist-info`` directory.

    Returns:
        str:
        The basename of the generated ``.whl`` file.
    """
    config = _get_config()

    return _run_build(
        build_type='editable',
        deps=_get_editable_package_dependencies(),
        dest_directory=wheel_directory,
        config_settings={
            'editable_mode': config.editable_mode,
            **(config_settings or {}),
        },
        metadata_directory=metadata_directory,
    )


def build_sdist(
    sdist_directory: str,
    config_settings: (ConfigSettings | None) = None,
) -> str:
    """Build a source distribution.

    This will perform the following steps:

    1. Write out the package dependencies to a file for setuptools to load.
    2. If configured, set up the NPM workspaces and install NPM packages.
    3. Run any package-defined build steps.
    4. Build the source distribution.

    Version Added:
        1.0

    Args:
        sdist_directory (str):
            The directory where the source distribution will be placed.

        config_settings (dict, optional):
            Any configuration settings to apply for the build.

    Returns:
        str:
        The basename of the generated ``.tar.gz`` file.
    """
    config = _get_config()

    return _run_build(
        build_type='sdist',
        deps=config.dependencies,
        dest_directory=sdist_directory,
        config_settings=config_settings,
    )


def build_wheel(
    wheel_directory: str,
    config_settings: (ConfigSettings | None) = None,
    metadata_directory: (str | None) = None,
) -> str:
    """Build a wheel distribution.

    This will perform the following steps:

    1. Write out the package dependencies to a file for setuptools to load.
    2. If configured, set up the NPM workspaces and install NPM packages.
    3. Run any package-defined build steps.
    4. Build the wheel distribution.

    Version Added:
        1.0

    Args:
        wheel_directory (str):
            The directory in which to place the wheel.

        config_settings (dict, optional):
            Any configuration settings to apply for the build.

        metadata_directory (str, optional):
            A custom path to the ``.dist-info`` directory.

    Returns:
        str:
        The basename of the generated ``.whl`` file.
    """
    config = _get_config()

    return _run_build(
        build_type='wheel',
        deps=config.dependencies,
        dest_directory=wheel_directory,
        config_settings=config_settings,
        metadata_directory=metadata_directory,
    )


def _get_config() -> PyProjectConfig:
    """Return configuration for the project.

    This will load the configuration on first call and then return that
    instance going forward.

    Version Added:
        1.0

    Returns:
        buildthings.config.PyProjectConfig:
        The :file:`pyproject.toml` configuration file state.
    """
    global _config

    if _config is None:
        _config = PyProjectConfig.from_file()

    return _config


def _get_isolated_build_dependencies(
    isolation_config: IsolationConfig,
) -> Sequence[str]:
    """Return the dependencies needed for an isolated build environment.

    These dependencies will be installed in the isolated build environment.

    This doesn't include any dependencies by default, other than those
    specified by ``build-system.requires``, but the following options can
    enable development dependencies and install-time dependencies:

    .. code-block:: toml

       [tool.buildthings.isolation]
       include-dev-deps = true
       include-install-deps = true
       exclude-deps = ['somedep']

    Any packages set to be excluded from installs will then be removed from
    the final list.

    Version Added:
        1.0

    Args:
        isolation_config (buildthings.config.IsolationConfig):
            The configuration for the isolation environment.

    Returns:
        list of str:
        The list of dependency specifiers.
    """
    config = _get_config()
    deps: list[str] = []

    if isolation_config['include_dev_deps']:
        deps += config.dev_dependencies

    if isolation_config['include_install_deps']:
        deps += config.dependencies

    # TODO: Normalize the dependencies on both sides of the comparison so we
    #       don't need exact dependency specifiers.
    if exclude_deps := set(isolation_config['exclude_deps']):
        deps = [
            dep
            for dep in deps
            if dep not in exclude_deps
        ]

    return deps


def _get_editable_package_dependencies() -> Sequence[str]:
    """Return the dependencies needed for an editable package.

    These dependencies will be installed in the isolated build environment.

    This includes the developer dependencies by default. If the package
    specifies that all dependencies should be included when building the
    package, those will be included as well.

    Any packages set to be excluded from editable installs will then be
    removed from the final list.

    Version Added:
        1.0

    Returns:
        list of str:
        The list of dependency specifiers.
    """
    config = _get_config()

    return [
        *config.dev_dependencies,
        *config.dependencies,
    ]


def _get_requires_for_build(
    *,
    build_type: BuildType,
    config_settings: ConfigSettings | None,
) -> Sequence[str]:
    """Return build-time requirements for a build type's isolated environment.

    This will return the standard dependencies for building the build type
    by default.

    Additional dependencies can be provided or modified by:

    .. code-block:: toml

       [tool.buildthings.isolation.editable]
       include-dev-deps = true
       include-install-deps = true
       exclude_deps = ['somedep']

    If any of the resulting dependencies are overriden by local dependencies
    found in :file:`.local-packages/`, then the local package paths will
    take precedence.

    Version Added:
        1.0

    Args:
        build_type (str):
            The build type being built.

        config_settings (dict, optional):
            Configuration settings to pass to the build backend.

    Returns:
        list of str:
        The list of build-time dependencies.
    """
    config = _get_config()
    isolation_config = config.isolation_build_configs[build_type]

    build_meta_func = getattr(_build_meta,
                              f'get_requires_for_build_{build_type}')

    # By default, this will just return what setuptools returns, which is
    # just the dependencies missing when calling setup.py (usually empty),
    # along with any extra dependencies that have been requested for the
    # environment (include-dev-deps and include-install-deps settings).
    return apply_local_dep_paths(
        local_packages_path=isolation_config['local_packages_path'],
        deps=[
            *_get_isolated_build_dependencies(isolation_config),
            *build_meta_func(config_settings),
        ],
    )


def _run_build(
    *,
    build_type: BuildType,
    deps: Sequence[str],
    dest_directory: str,
    config_settings: ConfigSettings | None,
    **kwargs,
) -> str:
    """Perform a build.

    This will perform the following steps:

    1. Write out the package dependencies to a file for setuptools to load.
    2. If configured, set up the NPM workspaces and install NPM packages.
    3. Run any package-defined build steps.
    4. Perform the build using the given configuration.

    Version Added:
        1.0

    Args:
        build_type (str):
            The type of build to perform.

        deps (list of str):
            The list of package dependencies to write.

        dest_directory (str):
            The directory in which to place the build.

        config_settings (dict):
            Any configuration settings to apply for the build.

        **kwargs (dict):
            Additional keyword arguments to pass to the parent backend's
            build function.

    Returns:
        str:
        The basename of the generated build file.
    """
    config = _get_config()

    _write_dependencies(deps)

    if config.use_npm:
        _rebuild_npm_workspaces()
        _install_npm_packages()

    _run_build_steps(config.extra_build_steps[build_type])

    build_func = getattr(_build_meta, f'build_{build_type}')

    try:
        return build_func(dest_directory, config_settings, **kwargs)
    finally:
        _cleanup()


def _rebuild_npm_workspaces() -> None:
    """Rebuild the links under .npm-workspaces for static media building.

    This will look up the module paths for any Python modules in
    ``tool.buildthings.npm.python-dependencies`` and link them so that
    JavaScript and CSS build infrastructure can import files correctly.

    Version Added:
        1.0
    """
    config = _get_config()

    # NOTE: Build backends run from within the root of the source tree.
    #       We could leave this as a relative path, but we'll make it
    #       absolute so there are no surprises.
    npm_workspaces_dir = os.path.join(os.getcwd(), '.npm-workspaces')

    if not os.path.exists(npm_workspaces_dir):
        os.mkdir(npm_workspaces_dir, 0o755)

    from importlib import import_module

    for mod_name in config.npm_python_deps:
        try:
            mod = import_module(mod_name)
        except ImportError:
            raise RuntimeError(
                f'Missing the dependency for {mod_name}, which is needed to '
                f'compile static media.'
            )

        mod_path = mod.__file__
        assert mod_path

        symlink_path = os.path.join(npm_workspaces_dir, mod_name)

        # Unlink this unconditionally, so we don't have to worry about things
        # like an existing dangling symlink that shows as non-existent.
        try:
            os.unlink(symlink_path)
        except FileNotFoundError:
            pass

        os.symlink(os.path.dirname(mod_path), symlink_path)


def _run_build_steps(
    steps: Sequence[BuildStep],
) -> None:
    """Run through build steps defined in the package.

    Each build step will be run within the context of the isolated build
    environment.

    This is supported by all build types.

    Version Added:
        1.0

    Args:
        steps (list of buildthings.config.BuildStep):
            Each build step to run.
    """
    for step in steps:
        command = step['command']
        command = command.replace('{python}', sys.executable)

        label = step.get('label') or f'Running {command}'

        logger.info(label)

        try:
            subprocess.check_call(command,
                                  shell=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f'Failed to run command {command!r}: {e}')


def _install_npm_packages() -> None:
    """Install NPM packages.

    Version Added:
        1.0

    Raises:
        RuntimeError:
            There was an error installing npm packages.
    """
    try:
        subprocess.run(
            ['npm', 'install'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f'Failed to install npm packages: {e.output}')


def _write_dependencies(
    deps: Sequence[str],
) -> None:
    """Write dependencies to a file.

    This will write to the package requirements file, so that
    :file:`pyproject.toml` can reference it.

    Version Added:
        1.0

    Args:
        deps (list of str, optional):
            The list of dependencies to write.
    """
    config = _get_config()

    dirname = os.path.dirname(config.package_deps_file)

    if not os.path.exists(dirname):
        os.makedirs(dirname, 0o755)

    with open(config.package_deps_file, 'w', encoding='utf-8') as fp:
        for dependency in deps:
            fp.write(f'{dependency}\n')


def _cleanup() -> None:
    """Perform any post-build cleanup.

    This will delete the generated package requirements file.

    Version Added:
        1.0
    """
    config = _get_config()
    package_deps_file = config.package_deps_file

    if os.path.exists(package_deps_file):
        os.unlink(package_deps_file)
