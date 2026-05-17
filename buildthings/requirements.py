"""Parsing support for requirements.txt-like files.

Version Added:
    1.0
"""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name

if TYPE_CHECKING:
    from collections.abc import Sequence


logger = logging.getLogger(__name__)


#: A regex for parsing comments in a requirements.txt.
#:
#: Version Added:
#:     1.0
COMMENT_RE = re.compile(r'#.*$')


def get_package_name_from_specifier(
    dep: str,
) -> str:
    """Return the name of a package from a dependency specifier.

    If the specifier includes extras (e.g., ``ReviewBoard[p4]``), then
    that will be included in the result for the package name.

    If the package can't be parsed, the name will be returned as-is and the
    failure will be logged.

    Version Added:
        1.1

    Args:
        dep (str):
            The dependency specifier.

    Returns:
        str:
        The package name.
    """
    try:
        requirement = Requirement(dep)
    except InvalidRequirement:
        logger.warning('Invalid dependency name %r', dep)

        return dep

    # We ensure a str because canonicalize_name returns a more specific (but
    # otherwise compatible) type for a str.
    name: str = canonicalize_name(requirement.name)

    if extras := requirement.extras:
        extras_str = ','.join(sorted(
            canonicalize_name(extra)
            for extra in extras
        ))
        name = f'{name}[{extras_str}]'

    return name


def filter_dependencies(
    deps: Sequence[str],
    *,
    exclude: set[str],
) -> list[str]:
    """Return a set of dependencies with specified packages excluded.

    This will process the provided list of dependencies and remove any that
    are found in ``exclude``.

    Package names are normalized for comparison, using the canonical package
    name rather than the form specified in either list.

    The exclude list is meant to be treated as a set of package names rather
    than specific versions. Any version specifiers will be stripped during
    comparison.

    Package names in either the list of dependencies or the exclude list may
    support ``[extras]``, but these must be an exact match. That is,
    ``reviewboard[p4]`` will match ``ReviewBoard[p4]``, but
    ``reviewboard[p4,ldap]`` will *not* match either ``ReviewBoard[p4]`` or
    ``ReviewBoard[ldap]``.

    Version Added:
        1.1

    Args:
        deps (list of str):
            The list of dependencies to filter.

        exclude (set of str):
            The dependencies to exclude.

    Returns:
        list of str:
        The resulting list of dependencies.
    """
    # Normalize all excluded dependency names.
    exclude_deps = {
        get_package_name_from_specifier(dep)
        for dep in exclude
    }

    return [
        dep
        for dep in deps
        if get_package_name_from_specifier(dep) not in exclude_deps
    ]


def parse_requirements_file(
    path: str,
) -> Sequence[str]:
    """Return valid dependency strings from a requirements.txt file.

    Only valid dependency specifiers will be returned. Items starting
    with ``-e``, ``-r``, `--index-url``, etc. will be skipped.

    Version Added:
        1.0

    Args:
        path (str):
            The path to the requirements file.

    Returns:
        list of str:
        The list of sanitized dependency specifiers.
    """
    with open(path, 'r', encoding='utf-8') as fp:
        return [
            parsed
            for line in fp
            if (parsed := _parse_requirement_line(line, path))
        ]


def _parse_requirement_line(
    line: str,
    path: str,
) -> str:
    """Parse a line from a requirements.txt file.

    This will remove any comments, validate the line as a valid requirement,
    and then return it if it passes validation.

    Version Added:
        1.0

    Args:
        line (str):
            The line to parse.

        path (str):
            The path to the file being processed.

    Returns:
        str:
        The sanitized requirement line, or an empty string if it fails to
        parse.
    """
    if line:
        line = (
            COMMENT_RE.sub('', line)
            .strip()
        )

        if line:
            try:
                Requirement(line)
            except InvalidRequirement:
                logger.warning('Skipping invalid dependency in %s: %r',
                               path, line)
                line = ''

    return line
