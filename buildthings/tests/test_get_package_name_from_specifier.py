"""Tests for buildthings.requirements.get_package_name_from_specifier.

Version Added:
    1.1
"""

from __future__ import annotations

import logging

from buildthings.requirements import get_package_name_from_specifier


def test_with_package_name() -> None:
    """Test get_package_name_from_specifier with a package name.

    Version Added:
        1.1
    """
    assert get_package_name_from_specifier('ReviewBoard') == 'reviewboard'


def test_with_version_specifier() -> None:
    """Test get_package_name_from_specifier with a version specifier.

    Version Added:
        1.1
    """
    assert get_package_name_from_specifier('ReviewBoard~=8.0') == 'reviewboard'


def test_with_extras() -> None:
    """Test get_package_name_from_specifier with [extras].

    Version Added:
        1.1
    """
    assert (get_package_name_from_specifier('ReviewBoard[P4]~=8.0') ==
            'reviewboard[p4]')


def test_with_extras_multiple() -> None:
    """Test get_package_name_from_specifier with [extras,extras].

    Version Added:
        1.1
    """
    assert (get_package_name_from_specifier('ReviewBoard[p4,LDAP]~=8.0') ==
            'reviewboard[ldap,p4]')


def test_with_invalid_specifier(caplog) -> None:
    """Test get_package_name_from_specifier with invalid specifier.

    Version Added:
        1.1
    """
    with caplog.at_level(logging.WARNING):
        assert (get_package_name_from_specifier('ReviewBoard[~=8/0') ==
                'ReviewBoard[~=8/0')

    assert "Invalid dependency name 'ReviewBoard[~=8/0'" in caplog.text
