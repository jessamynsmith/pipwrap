requirements-manager
====================

Requirements-manager simplifies handling Python project requirements across multiple environments.

- Create an rc file from a list of installed packages
- Generate a set of requirements files from an rc file

Setup
------------

::

    # Install package
    python setup.py install

Usage
-----

::

    # Interactively create .requirementsrc file from currently installed packages
    $ pip freeze > freeze.txt
    $ requirements_manager -c -p freeze.txt

    # Generate requirements files from .requirementsrc file
    $ requirements_manager -g
