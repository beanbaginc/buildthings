================================================
Buildthings: Python Setuptools with Super Powers
================================================

**Project:** |license-badge| |reviewed-badge|

**Latest release:** |latest-version-badge| |latest-pyvers-badge|


Buildthings is a Python build backend that extends Setuptools with features
needed for more advanced, interconnected applications, featuring:

* Editable installs using local source trees as dependencies

* Custom build steps for editable installs, source distributions, and
  wheels.

* Dynamic install-time and development-time dependency lists codified in
  Python.

* Built-in support for NPM-based build steps and embedded ``package.json``
  files.

This is built by Beanbag_ to help us build complex, production-ready
software, including:

* `Review Board <https://www.reviewboard.org>`_ -
  Extensible open source code and document review, one of
  the founders of the code review space

* `Djblets <https://github.com/djblets/djblets>`_ -
  Django production power tools


.. _Beanbag: https://beanbaginc.com
.. |latest-pyvers-badge| image:: https://img.shields.io/pypi/pyversions/buildthings
   :target: https://pypi.org/project/buildthings
.. |latest-version-badge| image:: https://img.shields.io/pypi/v/buildthings
   :target: https://pypi.org/project/buildthings
.. |license-badge| image:: https://img.shields.io/badge/license-MIT-green.svg
   :target: https://opensource.org/licenses/MIT
.. |reviewed-badge| image:: https://img.shields.io/badge/Review%20Board-d0e6ff?label=reviewed%20with
   :target: https://www.reviewboard.org


Using buildthings
=================

Buildthings is based on Setuptools, so all your existing Setuptools
settings will continue to work.

To switch to Buildthings, place the following at the top of your
``pyproject.toml``:

.. code-block:: toml

   [build-system]
   requires = ['buildthings']
   build-backend = 'buildthings.backend'


That's it! Now comes the cool part.


Configuration
=============

All buildthings settings live under ``[tool.buildthings]`` in your
``pyproject.toml``.


General Settings
----------------

tool.buildthings.dynamic
~~~~~~~~~~~~~~~~~~~~~~~~

A list of keys whose values should be loaded dynamically at build time via
one of:

* ``attr:`` (evaluated Python attribute/expression)
* ``file:`` (read from a text file).

Unless otherwise specified, all buildthings-specific configuration keys
may be dynamic.


**Example:**

.. code-block:: toml

   [tool.buildthings]
   dynamic = ["dependencies", "dev-dependencies"]

   dependencies = {attr = "mypackage.dependencies.install_requires"}
   dev-dependencies = {file = "dev-requirements.txt"}


Managing Dependencies
---------------------

tool.buildthings.dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A list of Python packages to install at install time.

This should be used *instead of* ``project.dependencies``.

Dependencies can also be installed in the isolated build environments using:
``tool.buildthings.isolation.include-install-deps`` or
``tool.buildthings.isolation.<build_type>.include-install-deps``. See
`Isolated Build Environments <isolated-environments>`_ below.

**Default:** The contents of ``requirements.txt`` will be read, if present.


**Examples:**

.. code-block:: toml

   [tool.buildthings]
   dependencies = [
       "housekeeping",
       "typelets",
   ]


You can also load this dynamically using ``attr:`` (a Python attribute path)
or ``file:`` (a text file):

.. code-block:: toml

   [tool.buildthings]
   dynamic = ["dependencies"]
   dependencies = {attr = "mypackage.dependencies.install_requires"}

or:

.. code-block:: toml

   [tool.buildthings]
   dynamic = ["dependencies"]
   dependencies = {file = "requirements.txt"}


tool.buildthings.dev-dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A list of additional development-focused Python packages that an editable
install should depend on.

These will not be used when building a Python wheel or source distribution.
They're a handy way of ensuring that an editable install has any optional
dependencies that may be needed while working on the codebase.

Development dependencies can also be installed in the isolated build
environments using:
``tool.buildthings.isolation.include-dev-deps`` or
``tool.buildthings.isolation.<build_type>.include-dev-deps``. See
`Isolated Build Environments <isolated-environments>`_ below.

**Default:** The contents of ``dev-requirements.txt`` will be read, if
present.


**Examples:**

.. code-block:: toml

   [tool.buildthings]
   dev-dependencies = [
       "kgb",
       "pytest",
       "sphinx",
   ]


Like ``dependencies``, this can be loaded dynamically:

.. code-block:: toml

   [tool.buildthings]
   dynamic = ["dev-dependencies"]
   dev-dependencies = {attr = "mypackage.dependencies.dev_requires"}

or:

.. code-block:: toml

   [tool.buildthings]
   dynamic = ["dev-dependencies"]
   dev-dependencies = {file = "dev-requirements.txt"}


.. _isolated-environments:

Isolated Build Environments
---------------------------

Python packages are built in isolated build environments. This usually
requires that all dependencies are available either from PyPI or in a
subdirectory.

Buildthings gives you control of this build environment by letting you
include development or install-time package dependencies automatically
as build-time dependencies, and by allowing you to point to local
development trees to supply any in-progres dependencies.

Defaults for all build types can be set in ``tool.buildthings.isolation``,
and overridden for each build type:

* ``tool.buildthings.isolation.editable``
* ``tool.buildthings.isolation.sdist``
* ``tool.buildthings.isolation.wheel``


tool.buildthings.isolation.local-packages-path
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The path to a directory containing symlinks to local development packages
needed for editable installs (including when this package is an editable
dependency of another).

Symlinks placed here point to the source trees of packages you are developing
locally, so that they will be used instead of attempting to find the
package in PyPI.

By default, this is only used for editable builds for a couple reasons:

1. Public builds must **never** depend on non-public packages.

2. When building packages using ``python -m build``, the wheel is generated
   from the source distribution, which won't contain your ``.local-packages``.

If you need to use local packages for testing (such as making sure you can
generate and install packages before all your source trees go live), do the
following:

1. Set ``local-packages-path`` to ``.local-packages`` (or another path).

2. Manually build sdists and wheels separately:

   .. code-block:: console

      $ python -m build --sdist .
      $ python -m build --wheel .

   This will ensure the wheel is built from your local tree and not the
   source distribution.

**Overridden by:**

* ``tool.buildthings.isolation.editable.local-packages-path``
* ``tool.buildthings.isolation.sdist.local-packages-path``
* ``tool.buildthings.isolation.wheel.local-packages-path``


**Defaults:**

* ``editable``: ``.local-packages``
* ``sdist``: None
* ``wheel``: None

**Examples:**

.. code-block:: toml

   [tool.buildthings.isolation]
   local-packages-path = ".prod-local-packages"

   [tool.buildthings.isolation.editable]
   local-packages-path = ".editable-local-packages"


Editable Installs
-----------------

tool.buildthings.isolation.include-dev-deps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When ``true``, development dependencies (from
``tool.buildthings.dev-dependencies`` or ``dev-requirements.txt``) will be
installed into the isolated build environment.

This may be needed if you're using extra build steps.

**Overridden by:**

* ``tool.buildthings.isolation.editable.include-dev-deps``
* ``tool.buildthings.isolation.sdist.include-dev-deps``
* ``tool.buildthings.isolation.wheel.include-dev-deps``

**Defaults:**

* ``editable``: ``false``
* ``sdist``: ``false``
* ``wheel``: ``false``

**Examples:**

.. code-block:: toml

   [tool.buildthings.isolation.editable]
   include-dev-deps = true


tool.buildthings.isolation.include-install-deps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When ``true``, install-time dependencies (from
``tool.buildthings.dependencies`` or ``requirements.txt``) will be installed
into the isolated build environment.

This may be needed if you're using extra build steps.

Defaults to ``false``.

**Overridden by:**

* ``tool.buildthings.isolation.editable.include-install-deps``
* ``tool.buildthings.isolation.sdist.include-install-deps``
* ``tool.buildthings.isolation.wheel.include-install-deps``

**Defaults:**

* ``editable``: ``false``
* ``sdist``: ``false``
* ``wheel``: ``false``

**Examples:**

.. code-block:: toml

   [tool.buildthings.isolation]
   include-install-deps = true

   [tool.buildthings.isolation.editable]
   include-install-deps = false


tool.buildthings.isolation.exclude-deps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A list of package names to exclude from the editable isolated build
environment's final list of dependencies.

This will filter out any depenencies that appear from using
``tool.buildthings.editable.isolation.include-dev-deps`` or
``tool.buildthings.editable.isolation.include-install-deps``.

**Overridden by:**

* ``tool.buildthings.isolation.editable.exclude-deps``
* ``tool.buildthings.isolation.sdist.exclude-deps``
* ``tool.buildthings.isolation.wheel.exclude-deps``

**Defaults:**

* ``editable``: ``[]``
* ``sdist``: ``[]``
* ``wheel``: ``[]``

**Examples:**

.. code-block:: toml

   [tool.buildthings.isolation.editable]
   exclude-deps = [
       "mysqldb",
   ]


Build Steps
-----------

Build steps let you run arbitrary shell commands as part of the build process.
They will run after buildthings's own steps are run, and before the
editable environment is set up or files are collected for a package.

Each step is either a plain command string or a table with a ``command`` key
and an optional ``label`` key:

.. code-block:: toml

   extra-build-steps = [
       "./scripts/do-things.sh",
       {command = "npm run build", label = "Building frontend assets"},
   ]


The special placeholder ``{python}`` is replaced at runtime with the path to
the Python interpreter used for the build:

.. code-block:: toml

   extra-build-steps = [
       "{python} manage.py collectstatic --noinput",
   ]


You may also specify these in their own array-like subsections:

.. code-block:: toml

   [[tool.buildthings.sdist.extra-build-steps]]
   label = "Do things"
   command = "./scripts/do-things.sh"

   [[tool.buildthings.sdist.extra-build-steps]]
   label = "Do more things"
   command = "./scripts/do-more-things.sh"


tool.buildthings.editable.extra-build-steps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Build steps run in an editable install. Use this for steps that should
help set up an editable environment (such as bootstrapping an SQLite
database or generating a settings file).

**Example:**

.. code-block:: toml

   [tool.buildthings.editable]
   extra-build-steps = [
       "./scripts/setup-environment.sh",
   ]


tool.buildthings.sdist.extra-build-steps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Build steps run when creating a source distribution (``sdist``).

**Example:**

.. code-block:: toml

   [tool.buildthings.sdist]
   extra-build-steps = [
       "pytest",
   ]


tool.buildthings.wheel.extra-build-steps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Build steps run when building a wheel.

**Example:**

.. code-block:: toml

   [tool.buildthings.wheel]
   extra-build-steps = [
       {command = "npm run build", label = "Building frontend assets"},
   ]


Building with NPM
-----------------

tool.buildthings.npm.enabled
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set to ``true`` to enable NPM support.

When enabled, buildthings can manage NPM workspaces that expose Python
packages as NPM-compatible modules, and will run ``npm install`` for you.

**Default:** ``false``

**Example:**

.. code-block:: toml

   [tool.buildthings.npm]
   enabled = true


tool.buildthings.npm.python-dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A list of Python package names to expose as NPM workspaces.

For each entry, buildthings creates a symlink under
``.npm-workspaces/`` that points to the Python dependency's module so that NPM
can resolve the package alongside your JavaScript dependencies. Each
module should include a ``package.json`` within it.

To use this, set the following in the ``package.json`` in the root of your
source tree:

.. code-block:: json

   {
       "workspaces": [
           ".npm-workspaces/*"
       ]
   }


**Example:**

.. code-block:: toml

   [tool.buildthings.npm]
   enabled = true
   python-dependencies = [
       "Djblets",
       "myproduct-frontend",
   ]


Our Other Projects
==================

* `Review Board`_ -
  Our dedicated open source code review product for teams of all sizes.

* `Housekeeping <https://github.com/beanbaginc/housekeeping>`_ -
  Deprecation management for Python modules, classes, functions, and
  attributes.

* `kgb <https://github.com/beanbaginc/kgb>`_ -
  A powerful function spy implementation to help write Python unit tests.

* `Registries <https://github.com/beanbaginc/python-registries>`_ -
  A flexible, typed implementation of the Registry Pattern for more
  maintainable and extensible codebases.

* `Typelets <https://github.com/beanbaginc/python-typelets>`_ -
  Type hints and utility objects for Python and Django projects.

You can see more on `github.com/beanbaginc <https://github.com/beanbaginc>`_
and `github.com/reviewboard <https://github.com/reviewboard>`_.
