from setuptools import setup

setup(
    name="requirements-manager",
    description="Manages pip requirements files for multiple environments",
    version="0.0.1",
    author="Jessamyn Smith",
    author_email="jessamyn.smith@gmail.com",
    url="https://github.com/jessamynsmith/requirements-manager",
    packages=["requirements_manager"],
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'requirements_manager = requirements_manager.requirements_manager:main',
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
