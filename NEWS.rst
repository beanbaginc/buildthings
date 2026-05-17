====================
Buildthings Releases
====================

Buildthings 1.1 (17-May-2026)
=============================

* Added support for dependencies lists and exclusions for each build type.

  The list of package dependencies can now be replaced for each build type,
  and exclusions can also be set. These can be set in the ``dependencies``
  and ``exclude-deps`` settings in the following sections:

  * ``tool.buildthings.editable``
  * ``tool.buildthings.sdist``
  * ``tool.buildthings.wheel``

* All ``exclude-deps`` settings will now match dependencies by canonical
  package name.

  Dependencies listed in ``exclude-deps`` (for both package and build
  dependencies) now compare canonical package names against those in the
  lists of dependencies. Any version specifiers will be ignored.

  If an excluded dependency has is in the form of ``package[extras]``,
  this will also match an equivalent extras specifier in the dependencies.

* Fixed building packages when being invoked by tox_.

  Most build frontends will run each backend hook in a separate subprocess,
  but tox_ (and its pyproject_api_) run them in a single process. This goes
  against PEP-517_ recommendations, but we now support it.


Buildthings 1.0.1 (31-March-2026)
=================================

* Existing symlinks in ``.npm-workspaces`` are now restored after the build
  completes or fails.


Buildthings 1.0 (27-March-2026)
===============================

* Initial public release.


.. _PEP-517: https://peps.python.org/pep-0517/
.. _pyproject-api: https://pypi.org/project/pyproject-api/
.. _tox: https://tox.wiki/
