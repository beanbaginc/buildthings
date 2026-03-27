"""Patches to setuptools to control behavior.

Version Added:
    1.0
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from setuptools.config.pyprojecttoml import _ConfigExpander

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence


#: Original initialization function for _ConfigExpander.
_old_ConfigExpander_init = _ConfigExpander.__init__


#: Whether _ConfigExpander has initialized.
#:
#: Version Added:
#:     1.0
_config_expander_initted = False


#: A list of functions to run after _ConfigExpander finishes initializing.
#:
#: Version Added:
#:     1.0
_config_expander_post_funcs: list[Callable[[_ConfigExpander], None]] = []


def patch_setuptools_package_deps(
    deps: Sequence[str],
) -> None:
    """Patch setuptools to set a static list of package dependencies.

    Version Added:
        1.0

    Args:
        deps (list of str):
            The list of dependencies to set.
    """
    if _config_expander_initted:
        raise AssertionError('Attempted to patch dependencies too late!')

    def _patch_deps(
        self: _ConfigExpander,
    ) -> None:
        if 'dependencies' in self.dynamic:
            self.dynamic.remove('dependencies')

        self.dynamic_cfg.pop('dependencies', None)
        self.project_cfg.setdefault('dependencies', []).extend(deps)

    _config_expander_post_funcs.append(_patch_deps)


def patch_setuptools() -> None:
    """Patch setuptools for buildthings customizations.

    Setuptools isn't built to be customizable, and has some hard-coded
    design elements that it gains from, well, monkey-patching distutils.

    We perform the same kind of patching on Setuptools to control some of
    the :file:`pyproject.toml` loading behavior in order to provide some
    control over the final package builds.

    Version Added:
        1.0
    """
    def _ConfigExpander_init(self, *args, **kwargs) -> None:
        global _config_expander_initted

        _old_ConfigExpander_init(self, *args, **kwargs)

        for func in _config_expander_post_funcs:
            func(self)

        _config_expander_initted = True

    assert _ConfigExpander.__init__ is _old_ConfigExpander_init, (
        'Attempted to patch _ConfigExpander.__init__ more than once!'
    )

    _ConfigExpander.__init__ = _ConfigExpander_init
