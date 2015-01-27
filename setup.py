from setuptools import setup, find_packages
import os.path as p

with open(p.join(p.dirname(__file__), 'requirements.txt'), 'r') as reqs:
    install_requires = [line.strip() for line in reqs]
with open(p.join(p.dirname(__file__), 'requirements_dev.txt'), 'r') as reqs:
    tests_require = [line.strip() for line in reqs]

setup(
    name="pipreq",
    version="0.1",
    author="Jessamyn Smith",
    author_email="jessamyn.smith@gmail.com",
    url="https://github.com/jessamynsmith/pipreq",
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
        'License :: OSI Approved :: MIT License',
        "Topic :: Software Development",
        "Topic :: Utilities",
    ])
