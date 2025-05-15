#!/usr/bin/env python
from setuptools import setup, find_packages

# Read version from __init__.py
import re
with open('src/doop/__init__.py', 'r') as f:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
    version = version_match.group(1) if version_match else '0.1.0'

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name="doop-lang",
    version=version,
    description="Document-Oriented Object Programming Language",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="tectix",
    author_email="tectix@example.com",
    url="https://github.com/tectix/doop-lang",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "doop=doop.cli:main",
        ],
    },
    install_requires=[
        "graphviz>=0.19.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Code Generators",
    ],
    python_requires=">=3.8",
)