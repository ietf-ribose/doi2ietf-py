import re
from os import environ

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    LONG_DESCRIPTION = fh.read()

PKG_VERSION = "0.1.0"

GIT_TAG = environ.get("GITHUB_REF", "")
TAG_VERSION = re.match(r'^refs/tags/v([0-9]+\.[0-9a-z]+\.[0-9a-z]+)$', GIT_TAG)

if TAG_VERSION:
    PKG_VERSION = TAG_VERSION.group(1)

setuptools.setup(
    name="doi2ietf",
    version=PKG_VERSION,
    author="Ribose",
    author_email="open.source@ribose.com",
    license='MIT',
    description="Converts DOI metadata into IETF BibXML format",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/ietf-ribose/doi2ietf-py",
    packages=['doi2ietf'],
    project_urls={
        'Documentation': 'https://github.com/ietf-ribose/doi2ietf-py',
        'Source': 'https://github.com/ietf-ribose/doi2ietf-py',
        'Tracker': 'https://github.com/ietf-ribose/doi2ietf-py/issues',
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
      'pyyaml',
      'requests',
      'requests-cache',
      'simplejson'
    ],
    tests_require=[
      'pytest',
      'lxml'
      'xmldiff',
    ],
    entry_points={
      'console_scripts': [
        'doi2ietf=doi2ietf.command_line:main',
    ],
},

)