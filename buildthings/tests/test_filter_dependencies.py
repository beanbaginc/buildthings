"""Tests for buildthings.requirements.filter_dependencies.

Version Added:
    1.1
"""

from __future__ import annotations

from buildthings.requirements import filter_dependencies


def test_with_exclude_empty() -> None:
    """Testing filter_dependencies with excluding empty set.

    Version Added:
        1.1
    """
    deps = filter_dependencies(
        [
            'buildthings',
            'kgb~=7.0',
            'ReviewBoard>=8.0',
        ],
        exclude=set(),
    )

    assert deps == [
        'buildthings',
        'kgb~=7.0',
        'ReviewBoard>=8.0',
    ]


def test_with_exclude_package_name() -> None:
    """Testing filter_dependencies with excluding package name.

    Version Added:
        1.1
    """
    deps = filter_dependencies(
        [
            'buildthings',
            'kgb~=7.0',
            'ReviewBoard>=8.0',
        ],
        exclude={
            'KGB',
        },
    )

    assert deps == [
        'buildthings',
        'ReviewBoard>=8.0',
    ]


def test_with_exclude_extras() -> None:
    """Testing filter_dependencies with excluding [extras].

    Version Added:
        1.1
    """
    deps = filter_dependencies(
        [
            'buildthings',
            'kgb~=7.0',
            'ReviewBoard>=8.0',
            'ReviewBoard[p4]',
        ],
        exclude={
            'buildthings[xyz]',
            'reviewboard[p4]',
        },
    )

    assert deps == [
        'buildthings',
        'kgb~=7.0',
        'ReviewBoard>=8.0',
    ]


def test_with_exclude_all() -> None:
    """Testing filter_dependencies with excluding all packages.

    Version Added:
        1.1
    """
    deps = filter_dependencies(
        [
            'buildthings',
            'kgb~=7.0',
            'ReviewBoard>=8.0',
        ],
        exclude={
            'buildthings',
            'kgb',
            'reviewboard',
        },
    )

    assert deps == []
