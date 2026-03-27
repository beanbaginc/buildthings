"""Parsing support for requirements.txt-like files.

Version Added:
    1.0
"""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

from packaging.requirements import InvalidRequirement, Requirement

if TYPE_CHECKING:
    from collections.abc import Sequence


logger = logging.getLogger(__name__)


#: A regex for parsing comments in a requirements.txt.
#:
#: Version Added:
#:     1.0
COMMENT_RE = re.compile(r'#.*$')


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
                logger.warning('Skipping invalid dependency in %s: %r\n',
                               path, line)
                line = ''

    return line
