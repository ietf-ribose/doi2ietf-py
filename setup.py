import re
from os import environ

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    LONG_DESCRIPTION = fh.read()

PKG_VERSION = "0.0.1"

GIT_TAG = environ.get("GITHUB_REF", "")
TAG_VERSION = re.match(r'^refs/tags/v([0-9]+\.[0-9a-z]+\.[0-9a-z]+)$', GIT_TAG)

if TAG_VERSION:
    PKG_VERSION = TAG_VERSION.group(1)

setuptools.setup(
    name="doi2ietf",
    version=PKG_VERSION,
    author="",
    author_email="",
    description="This is port of Ruby doilit script to Python 3",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/ietf-ribose/doi2ietf-py",
    project_urls={
        "Bug Tracker": "https://github.com/ietf-ribose/doi2ietf-py/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
