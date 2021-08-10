import setuptools
from os import environ

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

pkg_vesion = "0.0.1"
git_tag = environ.get('GITHUB_REF', None)

print('GIT TAG IN SETUP.PY:', git_tag)

setuptools.setup(
    name="doi2ietf",
    version=pkg_version,
    author="",
    author_email="",
    description="This is port of Ruby doilit script to Python 3",
    long_description=long_description,
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
    #install_requires=requirements,
)
