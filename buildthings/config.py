"""pyproject.toml configuration deserialization.

Version Added:
    1.0
"""

from __future__ import annotations

import os
import sys
from importlib import import_module
from typing import Literal, TYPE_CHECKING, TypedDict

from buildthings.requirements import parse_requirements_file

try:
    # Python >= 3.11
    from tomllib import load as load_toml
    _read_mode = 'rb'
except ImportError:
    # Python <= 3.10
    from toml import load as load_toml
    _read_mode = 'r'

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from typing import Any, Callable, NotRequired

    from typing_extensions import Self, TypeAlias

    _PyProjectConfigDict: TypeAlias = Mapping[str, Any]


#: A supported build type.
#:
#: Version Added:
#:     1.0
BuildType: TypeAlias = Literal['editable', 'sdist', 'wheel']


#: All supported build types.
#:
#: Version Added:
#:     1.0
ALL_BUILD_TYPES: Sequence[BuildType] = ['editable', 'sdist', 'wheel']


class BuildStep(TypedDict):
    """A custom build step for the package.

    Version Added:
        1.0
    """

    #: The command to run.
    command: str

    #: The optional label to display when running the command.
    label: NotRequired[str]


class IsolationConfig(TypedDict):
    """Configuration for an isolated build.

    Version Added:
        1.0
    """

    #: The list of dependencies to exclude from the isolated environment.
    exclude_deps: Sequence[str]

    #: Whether to include dev dependencies in the isolated environment.
    #:
    #: If set, all of the package's dependencies will be included as
    #: development dependencies when setting up the isolated environment.
    include_dev_deps: bool

    #: Whether to include package dependencies in the isolated environment.
    #:
    #: If set, all of the package's dependencies will be included as
    #: install-time dependencies when setting up the isolated environment.
    include_install_deps: bool

    #: The path to the local development Python packages.
    #:
    #: These are used for installing local packages in an isolated
    #: environment.
    #:
    #: If unset, local packages won't be used for the build type.
    local_packages_path: str | None


class PyProjectConfig:
    """A loaded pyproject.toml configuration file.

    This represents a :file:`pyproject.toml` file, with any buildthings
    settings loaded and deserialized, ready to build the package.

    Version Added:
        1.0
    """

    ######################
    # Instance variables #
    ######################

    #: The full deserialized pyproject.toml data.
    config: _PyProjectConfigDict

    #: The list of install-time dependencies.
    dependencies: Sequence[str]

    #: The list of editable-time development dependencies.
    dev_dependencies: Sequence[str]

    #: The set of all dynamic keys.
    dynamic: set[str]

    #: The editable mode used for the package.
    editable_mode: Literal['compat', 'lenient', 'strict']

    #: A list of extra build steps for each build type.
    extra_build_steps: Mapping[BuildType, Sequence[BuildStep]]

    #: The list of all files to collect for the package.
    files_to_collect: list[str]

    #: Build-specific configuration for isolated environments.
    isolation_build_configs: Mapping[BuildType, IsolationConfig]

    #: The list of Python packages required for NPM installs.
    #:
    #: Each of these will be set up as an NPM workspace, allowing any
    #: :file:`package.json` files in these packages to be used as
    #: dependencies for generating a :file:`node_modules` and running
    #: custom build steps.
    npm_python_deps: Sequence[str]

    #: Whether to manage an NPM install for the package.
    use_npm: bool

    @classmethod
    def from_file(
        cls,
        path: (str | None) = None,
    ) -> Self:
        """Return a loaded project configuration from a file.

        Args:
            path (str, optional):
                The path to load.

                If not provided, :file:`pyproject.toml` will be loaded.

        Returns:
            PyProjectConfig:
            The loaded configuration.
        """
        config = cls()
        config.load(path)

        return config

    def __init__(self) -> None:
        """Initialize the project configuration."""
        self.config = {}
        self.files_to_collect = []
        self.dynamic = set()
        self.dependencies = []
        self.dev_dependencies = []
        self.editable_mode = 'compat'
        self.extra_build_steps = {}
        self.isolation_build_configs = {}

        # NPM configuration.
        self.npm_python_deps = []
        self.use_npm = False

    def load(
        self,
        path: (str | None) = None,
    ) -> None:
        """Load a pyproject.toml file.

        This will attempt to load the :file:`pyproject.toml` file and parse
        it for any configuration needed for building the package.

        All configuration keys found in the file will be made available
        to any callers.

        Args:
            path (str, optional):
                The path to load.

                If not provided, :file:`pyproject.toml` will be loaded.
        """
        if not path:
            path = os.path.join(os.getcwd(), 'pyproject.toml')

        sys.path.insert(0, os.path.dirname(path))

        with open(path, _read_mode) as fp:
            self.config = load_toml(fp)

        # Load the common state.
        self._load_dynamic()
        self._load_dependencies()
        self._load_dev_dependencies()

        # Isolation configuration.
        isolation_common_config = self._load_isolation_options(
            build_type=None,
            default=IsolationConfig(
                exclude_deps=[],
                include_dev_deps=False,
                include_install_deps=False,
                local_packages_path=None,
            ),
        )

        isolation_defaults = {
            'editable': IsolationConfig(**{
                **isolation_common_config,
                'local_packages_path': '.local-packages',
            }),
        }

        self.isolation_build_configs = {
            build_type: self._load_isolation_options(
                build_type=build_type,
                default=isolation_defaults.get(build_type,
                                               isolation_common_config),
            )
            for build_type in ALL_BUILD_TYPES
        }

        # Build steps configuration.
        self.extra_build_steps = {
            build_type: self.load_config_value(
                full_key=f'tool.buildthings.{build_type}.extra-build-steps',
                default=[],
            )
            for build_type in ALL_BUILD_TYPES
        }

        # Editable configuration.
        editable_mode = self.load_config_value(
            full_key='tool.buildthings.editable.install-mode',
            default=self.editable_mode,
        )

        if editable_mode not in {'compat', 'lenient', 'strict'}:
            raise ValueError(
                'tool.buildthings.editable.install-mode must be one of: '
                'compat, lenient, strict'
            )

        self.editable_mode = editable_mode

        # NPM configuration.
        self.use_npm = self.load_config_value(
            full_key='tool.buildthings.npm.enabled',
            default=self.use_npm,
        )

        self.npm_python_deps = self.load_config_value(
            full_key='tool.buildthings.npm.python-dependencies',
            default=self.npm_python_deps,
        )

    def load_config_value(
        self,
        *,
        full_key: str,
        allow_dynamic: bool = True,
        default: Any = None,
        file_loader: (Callable[[str], Any] | None) = None,
    ) -> Any:
        """Load a value from a configuration key.

        This can load a key specified as a dotted path within the
        deserialized configuration data.

        If the key is marked as a dynamic configuration key, this will
        take care of loading the corresponding value either from the
        specified attribute or file.

        Args:
            full_key (str):
                The full key to load.

            allow_dynamic (bool, optional):
                Whether this key's value is allowed to be specified
                dynamically.

            default (object, optional):
                The default value to return if a key was not found.

            file_loader (callable, optional):
                The file loader used to load dynamic file specifiers, if any.

        Returns:
            object:
            The loaded value.

        Raises:
            ValueError:
                A configuration setting did not meet expectations.

                Details will be in the error message.
        """
        key_parts = full_key.split('.')
        key = key_parts[-1]

        try:
            config_value = self._load_key_dotted(self.config, key_parts)
        except KeyError:
            return default

        is_dynamic = key in self.dynamic

        if not is_dynamic:
            return config_value

        if not allow_dynamic:
            raise ValueError(
                f'Key "{key}" cannot be specified in project.dynamic='
            )

        if not isinstance(config_value, dict):
            raise ValueError(
                f'Dynamic key "{full_key}" must be a dictionary with "attr" '
                f'or "file" keys in pyproject.toml.'
            )

        has_attr = 'attr' in config_value
        has_file = 'file' in config_value

        if not has_attr and not has_file:
            # This is missing an "attr" or "file" key.
            raise ValueError(
                f'Missing key "attr" or "file" for dynamic key '
                f'"{full_key}" in pyproject.toml.'
            )
        elif has_attr and has_file:
            # This includes both an "attr" and "file" key.
            raise ValueError(
                f'Only one of "attr" or "file" may be specified for '
                f'dynamic key "{full_key}" in pyproject.toml.'
            )
        elif has_attr:
            # There's an "attr" key. Load the specified object and attribute
            # represented by the Python path.
            attr_value = config_value['attr']
            mod_path, attr_name = attr_value.rsplit('.', 1)

            try:
                module = import_module(mod_path)
            except Exception as e:
                raise ValueError(
                    f'Unable to load dynamic module attribute "{attr_value}": '
                    f'{e}'
                )

            result = getattr(module, attr_name)

            if result is not None and callable(result):
                result = result()

            return result
        elif has_file:
            # Theres a "file" key. Load the file and run it through the
            # specified parser.
            assert file_loader is not None

            file_value = os.path.abspath(config_value['file'])

            try:
                return self._load_file(
                    path=file_value,
                    file_loader=file_loader,
                )
            except IOError as e:
                raise IOError(
                    f'Unable to read "{file_value}" (specified as '
                    f'key "{full_key}" in pyproject.toml): {e}:'
                )

        raise AssertionError('Not reached')

    def _load_file(
        self,
        path: str,
        *,
        file_loader: Callable[[str], Any],
    ) -> Any:
        """Load contents from a file.

        This will attempt to load a file and run it through the provided
        file loader. If successful, the file will be marked as a file to
        collect when packaging.

        It's up to the caller to check for any exceptions raised by the
        file loader.

        Args:
            path (str):
                The file path to load.

            file_loader (callable):
                The function used to load and return contents from the file.

        Raises:
            Exception:
                Any exception raised by the file loader.
        """
        result = file_loader(path)
        self.files_to_collect.append(path)

        return result

    def _load_dynamic(self) -> None:
        """Load the set of all dynamic configuration keys.

        This will look in ``tool.buildthings.dynamic`` for configuration keys
        that should be looked up through a Python import.
        """
        dynamic: set[str] = set()

        try:
            dynamic.update(self._load_key_dotted(
                self.config,
                ('project', 'dynamic'),
            ))
        except KeyError:
            pass

        try:
            dynamic.update(self._load_key_dotted(
                self.config,
                ('tool', 'buildthings', 'dynamic'),
            ))
        except KeyError:
            pass

        self.dynamic = dynamic

    def _load_dependencies(self) -> None:
        """Load a list of dependencies.

        This is loaded from ``tool.buildthings.dependencies``. If not found,
        this will look for a :file:`requirements.txt` and try to load from
        that.

        Raises:
            ValueError:
                A dependency configuration setting did not meet expectations.

                Details will be in the error message.
        """
        result = self.load_config_value(
            full_key='tool.buildthings.dependencies',
            file_loader=parse_requirements_file,
        )

        if result is None:
            try:
                result = self._load_file(
                    'requirements.txt',
                    file_loader=parse_requirements_file,
                )
            except IOError:
                # We were optimistically looking for this, so just ignore
                # the error.
                result = []
        elif not isinstance(result, list):
            raise ValueError(
                f'Key "tool.buildthings.dependencies" must resolve to a '
                f'list of dependencies (not {result!r}). Did you forget to '
                f'list this in "tool.buildthings.dynamic"?'
            )

        self.dependencies = result or []

    def _load_dev_dependencies(self) -> None:
        """Load a list of development dependencies.

        These are meant for use at editable time.

        This is loaded from ``tool.buildthings.dev-dependencies``. If not
        found, this will look for a :file:`dev-requirements.txt` and try
        to load from that.

        Raises:
            ValueError:
                A dependency configuration setting did not meet expectations.

                Details will be in the error message.
        """
        result = self.load_config_value(
            full_key='tool.buildthings.dev-dependencies',
            file_loader=parse_requirements_file,
        )

        if result is None:
            try:
                result = self._load_file(
                    'dev-requirements.txt',
                    file_loader=parse_requirements_file,
                )
            except IOError:
                # We were optimistically looking for this, so just ignore
                # the error.
                result = []
        elif not isinstance(result, list):
            raise ValueError(
                f'Key "tool.buildthings.dev-dependencies" must resolve to a '
                f'list of dependencies (not {result!r}). Did you forget to '
                f'list this in "tool.buildthings.dynamic"?'
            )

        self.dev_dependencies = result

    def _load_isolation_options(
        self,
        *,
        build_type: str | None,
        default: IsolationConfig,
    ) -> IsolationConfig:
        """Load configuration for an isolated environment.

        Args:
            build_type (str):
                The build type, or ``None`` to reference common options.

            default (IsolationConfig):
                The default values for each option.

        Returns:
            IsolationConfig:
            The loaded configuration.
        """
        prefix = 'tool.buildthings.isolation'

        if build_type:
            prefix = f'{prefix}.{build_type}'

        return IsolationConfig(
            exclude_deps=self.load_config_value(
                full_key=f'{prefix}.exclude-deps',
                default=default['exclude_deps'],
            ),
            include_dev_deps=self.load_config_value(
                full_key=f'{prefix}.include-dev-deps',
                default=default['include_dev_deps'],
            ),
            include_install_deps=self.load_config_value(
                full_key=f'{prefix}.include-install-deps',
                default=default['include_install_deps'],
            ),
            local_packages_path=self.load_config_value(
                full_key=f'{prefix}.local-packages-path',
                default=default['local_packages_path'],
            ),
        )

    def _load_key_dotted(
        self,
        d: Mapping[str, Any],
        keys: Sequence[str],
    ) -> Any:
        """Return a value from a mapping given a dotted path.

        Args:
            d (dict):
                The dictionary to load from.

            keys (list of str):
                The list of key path components.

        Returns:
            object:
            The resulting value.
        """
        for key in keys:
            d = d[key]

        return d
