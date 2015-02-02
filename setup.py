from setuptools import setup, find_packages
import os.path as p

with open(p.join(p.dirname(__file__), 'requirements', 'package.txt'), 'r') as reqs:
    install_requires = [line.strip() for line in reqs]

tests_require = []
try:
    with open(p.join(p.dirname(__file__), 'requirements', 'test.txt'), 'r') as reqs:
        tests_require = [line.strip() for line in reqs]
except IOError:
    pass

setup(
    name="pipreq",
    version="0.1",
    author="Jessamyn Smith",
    author_email="jessamyn.smith@gmail.com",
    url="https://github.com/jessamynsmith/pipreq",
    license='MIT',
    description="Manages pip requirements files for multiple environments",
    keywords=['pip', 'requirements', 'heroku', 'development', 'production'],

    install_requires=install_requires,
    tests_require=tests_require,

    packages=find_packages(exclude=['*test*']),

    entry_points={
        'console_scripts': [
            'pipreq = pipreq.cli:main'
        ],
    },

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: MIT License',
        "Topic :: Software Development",
        "Topic :: Utilities",
    ])
