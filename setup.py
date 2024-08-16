#!/usr/bin/python
# coding: utf-8
import os
from setuptools import setup, find_packages

cur_dir = os.path.abspath(os.path.dirname(__file__))


def read(path):
    with open(path, "r") as _file:
        return _file.read()


def read_req(name):
    path = os.path.join(cur_dir, name)
    return [req.strip() for req in read(path).splitlines() if req.strip()]


version_ns = {}
with open(os.path.join(cur_dir, "version.py")) as f:
    exec(f.read(), {}, version_ns)


long_description = open("README.rst").read()
setup(
    name="publishing-tools",
    version=version_ns["__version__"],
    long_description=long_description,
    description="Tools that can be used for publishing/releasing packages and container images.",
    long_description_content_type="text/x-rst",
    author="Rasmus Munk",
    author_email="munk1@live.dk",
    packages=find_packages(),
    url="https://github.com/rasmunk/publishing-tools",
    license="MIT",
    keywords=[
        "Publishing",
        "Signature",
        "Checksum",
        "Verification",
        "Packages",
        "Container Images",
    ],
    install_requires=read_req("requirements.txt"),
    extras_require={
        "dev": read_req("requirements-dev.txt"),
    },
    entry_points={
        "console_scripts": [
            "sign = publish.cli.sign:cli",
            "verify = publish.cli.verify:cli",
            "publish = publish.cli.publish:cli",
        ]
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
