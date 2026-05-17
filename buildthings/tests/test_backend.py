"""Tests for buildthings.backend.

Version Added:
    1.1
"""

from __future__ import annotations

from importlib.metadata import Distribution

from buildthings.tests.utils import (get_dist_from_wheel,
                                     setup_backend)


#
# Tests for get_requires_for_build_editable.
#

def test_get_requires_for_build_editable() -> None:
    """Test get_requires_for_build_editable.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]
    """

    with setup_backend(pyproject_toml) as backend:
        deps = backend.get_requires_for_build_editable()

    assert deps == []


def test_get_requires_for_build_editable_with_include_install_deps() -> None:
    """Test get_requires_for_build_editable with include-install-deps=true.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]

        [tool.buildthings.isolation.editable]
        include-install-deps = true
    """

    with setup_backend(pyproject_toml) as backend:
        deps = backend.get_requires_for_build_editable()

    assert deps == [
        'Djblets~=100.9',
        'ReviewBoard[p4]',
    ]


def test_get_requires_for_build_editable_with_include_dev_deps() -> None:
    """Test get_requires_for_build_editable with include-dev-deps=true

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]

        [tool.buildthings.isolation.editable]
        include-dev-deps = true
    """

    with setup_backend(pyproject_toml) as backend:
        deps = backend.get_requires_for_build_editable()

    assert deps == [
        'grumble',
        'kgb~=7.0',
    ]


def test_get_requires_for_build_editable_with_include_all_deps() -> None:
    """Test get_requires_for_build_editable with include-dev-deps=true and
    include-install-deps=true.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]

        [tool.buildthings.isolation.editable]
        include-install-deps = true
        include-dev-deps = true
    """

    with setup_backend(pyproject_toml) as backend:
        deps = backend.get_requires_for_build_editable()

    assert deps == [
        'grumble',
        'kgb~=7.0',
        'Djblets~=100.9',
        'ReviewBoard[p4]',
    ]


def test_get_requires_for_build_editable_with_exclude_deps() -> None:
    """Test get_requires_for_build_editable with exclude-deps.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]

        [tool.buildthings.isolation.editable]
        include-install-deps = true
        include-dev-deps = true
        exclude-deps = ['djblets', 'kgb']
    """

    with setup_backend(pyproject_toml) as backend:
        deps = backend.get_requires_for_build_editable()

    assert deps == [
        'grumble',
        'ReviewBoard[p4]',
    ]


#
# Tests for get_requires_for_build_sdist.
#

def test_get_requires_for_build_sdist() -> None:
    """Test get_requires_for_build_sdist.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]
    """

    with setup_backend(pyproject_toml) as backend:
        deps = backend.get_requires_for_build_sdist()

    assert deps == []


def test_get_requires_for_build_sdist_with_include_install_deps() -> None:
    """Test get_requires_for_build_sdist with include-install-deps=true.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]

        [tool.buildthings.isolation.sdist]
        include-install-deps = true
    """

    with setup_backend(pyproject_toml) as backend:
        deps = backend.get_requires_for_build_sdist()

    assert deps == [
        'Djblets~=100.9',
        'ReviewBoard[p4]',
    ]


def test_get_requires_for_build_sdist_with_include_dev_deps() -> None:
    """Test get_requires_for_build_sdist with include-dev-deps=true.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]

        [tool.buildthings.isolation.sdist]
        include-dev-deps = true
    """

    with setup_backend(pyproject_toml) as backend:
        deps = backend.get_requires_for_build_sdist()

    assert deps == [
        'grumble',
        'kgb~=7.0',
    ]


def test_get_requires_for_build_sdist_with_include_all_deps() -> None:
    """Test get_requires_for_build_sdist with include-dev-deps=true and
    include-install-deps=true.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]

        [tool.buildthings.isolation.sdist]
        include-install-deps = true
        include-dev-deps = true
    """

    with setup_backend(pyproject_toml) as backend:
        deps = backend.get_requires_for_build_sdist()

    assert deps == [
        'grumble',
        'kgb~=7.0',
        'Djblets~=100.9',
        'ReviewBoard[p4]',
    ]


def test_get_requires_for_build_sdist_with_exclude_deps() -> None:
    """Test get_requires_for_build_sdist with exclude-deps.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]

        [tool.buildthings.isolation.sdist]
        include-install-deps = true
        include-dev-deps = true
        exclude-deps = ['djblets', 'kgb']
    """

    with setup_backend(pyproject_toml) as backend:
        deps = backend.get_requires_for_build_sdist()

    assert deps == [
        'grumble',
        'ReviewBoard[p4]',
    ]


#
# Tests for get_requires_for_build_wheel.
#

def test_get_requires_for_build_wheel() -> None:
    """Test get_requires_for_build_wheel.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]
    """

    with setup_backend(pyproject_toml) as backend:
        deps = backend.get_requires_for_build_wheel()

    assert deps == []


def test_get_requires_for_build_wheel_with_include_install_deps() -> None:
    """Test get_requires_for_build_wheel with include-install-deps=true.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]

        [tool.buildthings.isolation.wheel]
        include-install-deps = true
    """

    with setup_backend(pyproject_toml) as backend:
        deps = backend.get_requires_for_build_wheel()

    assert deps == [
        'Djblets~=100.9',
        'ReviewBoard[p4]',
    ]


def test_get_requires_for_build_wheel_with_include_dev_deps() -> None:
    """Test get_requires_for_build_wheel with include-dev-deps=true.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]

        [tool.buildthings.isolation.wheel]
        include-dev-deps = true
    """

    with setup_backend(pyproject_toml) as backend:
        deps = backend.get_requires_for_build_wheel()

    assert deps == [
        'grumble',
        'kgb~=7.0',
    ]


def test_get_requires_for_build_wheel_with_include_all_deps() -> None:
    """Test get_requires_for_build_wheel with include-dev-deps=true and
    include-install-deps=true.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]

        [tool.buildthings.isolation.wheel]
        include-install-deps = true
        include-dev-deps = true
    """

    with setup_backend(pyproject_toml) as backend:
        deps = backend.get_requires_for_build_wheel()

    assert deps == [
        'grumble',
        'kgb~=7.0',
        'Djblets~=100.9',
        'ReviewBoard[p4]',
    ]


def test_get_requires_for_build_wheel_with_exclude_deps() -> None:
    """Test get_requires_for_build_wheel with exclude-deps.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]

        [tool.buildthings.isolation.wheel]
        include-install-deps = true
        include-dev-deps = true
        exclude-deps = ['djblets', 'kgb']
    """

    with setup_backend(pyproject_toml) as backend:
        deps = backend.get_requires_for_build_wheel()

    assert deps == [
        'grumble',
        'ReviewBoard[p4]',
    ]


#
# Tests for prepare_metadata_for_build_editable.
#

def test_prepare_metadata_for_build_editable() -> None:
    """Test prepare_metadata_for_build_editable.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]
    """

    with setup_backend(pyproject_toml) as backend:
        path = backend.prepare_metadata_for_build_editable(
            metadata_directory='.',
        )

        assert path == 'buildthings_test-1.0.dist-info'
        assert Distribution.at(path).requires == [
            'grumble',
            'kgb~=7.0',
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]


def test_prepare_metadata_for_build_editable_with_build_type_deps() -> None:
    """Test prepare_metadata_for_build_editable with build type dependencies
    override.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]

        [tool.buildthings.editable]
        dependencies = [
            'Djblets>=200',
        ]
    """

    with setup_backend(pyproject_toml) as backend:
        path = backend.prepare_metadata_for_build_editable(
            metadata_directory='.',
        )

        assert path == 'buildthings_test-1.0.dist-info'
        assert Distribution.at(path).requires == [
            'grumble',
            'kgb~=7.0',
            'Djblets>=200',
        ]


def test_prepare_metadata_for_build_editable_with_exclude_deps() -> None:
    """Test prepare_metadata_for_build_editable with build type
    exclude-deps.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
            'ReviewBoard>=90',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]

        [tool.buildthings.editable]
        exclude-deps = [
            'reviewboard',
            'kgb',
        ]
    """

    with setup_backend(pyproject_toml) as backend:
        path = backend.prepare_metadata_for_build_editable(
            metadata_directory='.',
        )

        assert path == 'buildthings_test-1.0.dist-info'
        assert Distribution.at(path).requires == [
            'grumble',
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]


#
# Tests for prepare_metadata_for_build_wheel.
#

def test_prepare_metadata_for_build_wheel() -> None:
    """Test prepare_metadata_for_build_wheel.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]
    """

    with setup_backend(pyproject_toml) as backend:
        path = backend.prepare_metadata_for_build_wheel(
            metadata_directory='.',
        )

        assert path == 'buildthings_test-1.0.dist-info'
        assert Distribution.at(path).requires == [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]


def test_prepare_metadata_for_build_wheel_with_build_type_deps() -> None:
    """Test prepare_metadata_for_build_wheel with build type dependencies
    override.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]

        [tool.buildthings.wheel]
        dependencies = [
            'Djblets>=200',
        ]
    """

    with setup_backend(pyproject_toml) as backend:
        path = backend.prepare_metadata_for_build_wheel(
            metadata_directory='.',
        )

        assert path == 'buildthings_test-1.0.dist-info'
        assert Distribution.at(path).requires == [
            'Djblets>=200',
        ]


def test_prepare_metadata_for_build_wheel_with_exclude_deps() -> None:
    """Test prepare_metadata_for_build_wheel with build type exclude-deps.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
            'ReviewBoard>=90',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]

        [tool.buildthings.wheel]
        exclude-deps = [
            'reviewboard',
            'kgb',
        ]
    """

    with setup_backend(pyproject_toml) as backend:
        path = backend.prepare_metadata_for_build_wheel(
            metadata_directory='.',
        )

        assert path == 'buildthings_test-1.0.dist-info'
        assert Distribution.at(path).requires == [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]


#
# Tests for build_editable.
#

def test_build_editable() -> None:
    """Test build_editable.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]
    """

    with setup_backend(pyproject_toml) as backend:
        path = backend.build_editable(wheel_directory='.')
        assert path == 'buildthings_test-1.0-0.editable-py3-none-any.whl'

        dist = get_dist_from_wheel(path)

        assert dist.requires == [
            'grumble',
            'kgb~=7.0',
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]


def test_build_editable_with_build_type_deps() -> None:
    """Test build_editable with build type dependencies override.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]

        [tool.buildthings.editable]
        dependencies = [
            'Djblets>=200',
        ]
    """

    with setup_backend(pyproject_toml) as backend:
        path = backend.build_editable(wheel_directory='.')
        assert path == 'buildthings_test-1.0-0.editable-py3-none-any.whl'

        dist = get_dist_from_wheel(path)

        assert dist.requires == [
            'grumble',
            'kgb~=7.0',
            'Djblets>=200',
        ]


def test_build_editable_with_exclude_deps() -> None:
    """Test build_editable with build type exclude-deps.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
            'ReviewBoard>=90',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]

        [tool.buildthings.editable]
        exclude-deps = [
            'reviewboard',
            'kgb',
        ]
    """

    with setup_backend(pyproject_toml) as backend:
        path = backend.build_editable(wheel_directory='.')
        assert path == 'buildthings_test-1.0-0.editable-py3-none-any.whl'

        dist = get_dist_from_wheel(path)

        assert dist.requires == [
            'grumble',
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]


#
# Tests for build_wheel.
#

def test_build_wheel() -> None:
    """Test build_wheel.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]
    """

    with setup_backend(pyproject_toml) as backend:
        path = backend.build_wheel(wheel_directory='.')
        assert path == 'buildthings_test-1.0-py3-none-any.whl'

        dist = get_dist_from_wheel(path)

        assert dist.requires == [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]


def test_build_wheel_with_build_type_deps() -> None:
    """Test build_wheel with build type dependencies override.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]

        [tool.buildthings.wheel]
        dependencies = [
            'Djblets>=200',
        ]
    """

    with setup_backend(pyproject_toml) as backend:
        path = backend.build_wheel(wheel_directory='.')
        assert path == 'buildthings_test-1.0-py3-none-any.whl'

        dist = get_dist_from_wheel(path)

        assert dist.requires == [
            'Djblets>=200',
        ]


def test_build_wheel_with_exclude_deps() -> None:
    """Test build_wheel with build type exclude-deps.

    Version Added:
        1.1
    """
    pyproject_toml = """
        [tool.buildthings]
        dependencies = [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
            'ReviewBoard>=90',
        ]
        dev-dependencies = [
            'grumble',
            'kgb~=7.0',
        ]

        [tool.buildthings.wheel]
        exclude-deps = [
            'reviewboard',
            'kgb',
        ]
    """

    with setup_backend(pyproject_toml) as backend:
        path = backend.build_wheel(wheel_directory='.')
        assert path == 'buildthings_test-1.0-py3-none-any.whl'

        dist = get_dist_from_wheel(path)

        assert dist.requires == [
            'Djblets~=100.9',
            'ReviewBoard[p4]',
        ]
