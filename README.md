pipreq
======

pipreq simplifies handling Python project requirements across multiple environments.
pip freeze > requirements.txt gets your project started, but do you really want
mock, coverage, etc. installed on your production server? If, like me, you've ever
found yourself sifting through the output of pip freeze trying to figure out what
packages you've installed but didn't yet add to one of your requirements files, then
pipreq is the tool for you.

Features
--------

- Inspect a list of packages and create or update a requirements rc file
- Generate a set of requirements files from an rc file

[![Build Status](https://travis-ci.org/jessamynsmith/pipreq.svg?branch=master)](https://travis-ci.org/jessamynsmith/pipreq)

Installation
------------

The development version can be installed with:

    pip install -e git://github.com/jessamynsmith/pipreq.git#egg=pipreq

If you are developing locally, your version can be installed from the working directory with:

    python setup.py.install

Usage
-----

pipreq uses an rc file to track requirements. You create a section for each requirements file,
and (if desired) select one section to be shared. The default configuration is as follows:

```
# .requirementsrc
[metadata]
shared = common

[common]

[development]

[production]
```

This would result in the following requirements directory structure:

    requirements/
        common.txt
        development.txt
        production.txt

where development.txt and production.txt both include the line "-r common.txt"

** Getting Started with pipreq **

1. (Optional) Create an empty .requirementsrc file with your desired metadata and sections

2. Interactively create .requirementsrc file from currently installed packages:

    pip freeze > freeze.txt
    pipreq -c -p freeze.txt

3. Generate requirements files from .requirementsrc file:

    pipreq -g

4. Create a top-level requirements.txt file that points to your production requirements, e.g.
"-r production.txt"

** Keeping requirements up to date with pipreq **

1. Interactively update .requirementsrc file from currently installed packages:

    pip freeze > freeze.txt
    pipreq -c -p freeze.txt

2. Re-generate requirements files from .requirementsrc file:

    pipreq -g


Development
-----

Fork the project on github and git clone your fork, e.g.:

    git clone https://github.com/<username>/pipreq.git

Create a virtualenv and install dependencies:

    mkvirtualenv pipreq
    pip install -r requirements.txt -r requirements_test.txt

Run tests and view coverage:

    coverage run -m nose
    coverage report

Check code style:

    flake8 . --max-line-length=100

Install your local copy:

    python setup.py.install
