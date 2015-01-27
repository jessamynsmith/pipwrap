pipreq
======

pipreq simplifies handling Python project requirements across multiple environments.

- Create an rc file from a list of installed packages
- Generate a set of requirements files from an rc file

Setup
-----

::

The development version can be installed with:

    pip install -e git://github.com/jessamynsmith/pipreq.git#egg=pipreq

If you are developing locally, your version can be installed from the working directory with:

    python setup.py.install

Usage
-----

::

Interactively create .requirementsrc file from currently installed packages

    pip freeze > freeze.txt
    pipreq -c -p freeze.txt

Generate requirements files from .requirementsrc file

    pipreq -g

Development
-----

::

Fork the project on github and git clone your fork, e.g.:

    git clone https://github.com/<username>/pipreq.git

Create a virtualenv and install dependencies:

    mkvirtualenv pipreq
    pip install -r requirements.txt -r requirements_dev.txt

Run tests and view coverage:

    coverage run -m nose
    coverage report

Check code style:

    flake8 . --max-line-length=100

Install your local copy:

    python setup.py.install
