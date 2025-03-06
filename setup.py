#!/usr/bin/env python
# Always prefer setuptools over distutils
from __future__ import print_function, unicode_literals

from codecs import open
import glob
from multiprocessing import Process, Pipe
from os import path
import os
import subprocess
import sys

from pipenv.project import Project
from pipenv.routines.requirements import generate_requirements
from pipenv.utils.dependencies import get_lockfile_section_using_pipfile_category
from pipenv.utils.requirements import requirements_from_lockfile
from setuptools import setup, find_packages


__author__ = "jingyu.wy"


def get_pipfile_requirements() -> list[str]:
    project = Project()
    lockfile = project.load_lockfile(expand_env_vars=False)
    pipfile_root_package_names = project.pipfile_package_names["combined"]

    deps = {}
    default_deps = lockfile["default"]
    default_deps = {
        k: v
        for k, v in default_deps.items()
        if k in pipfile_root_package_names
    }
    deps.update(default_deps)

    pip_installable_lines = requirements_from_lockfile(
        deps, include_hashes=False, include_markers=False
    )

    return  pip_installable_lines


def main():
    try:
        requirements = get_pipfile_requirements()
        with open("requirements.txt", 'w') as file:
            for requirement in requirements:
                file.write(requirement)
    except FileNotFoundError:
        requirements = []

    try:
        with open("README.md", 'r') as file:
            readme = file.read()
    except FileNotFoundError:
        readme = ""

    try:
        with open("LICENSE", 'r') as file:
            _license = file.read()
    except FileNotFoundError:
        _license = ""

    setup(
        name='ansible_apsarastack',
        setuptools_git_versioning={
            "enabled": True,
            "tag_filter": "versions/(?P<tag>.*)",
        },
        packages=find_packages(where="src", include=["ansible.module_utils", "ansible.modules.cloud.apsarastack"]),
        package_dir={"": "src"},
        package_data={
            '': ['requirements.txt', 'README.md', 'LICENSE'],
        },
        # url='',
        install_requires=requirements,
        license=_license,
        zip_safe=False,
        keywords='ansible_apsarastack',
        author='Wang Yu',
        author_email='jingyu.wy@alibaba-inc.com',
        description='Ansible provider for Apsarastack.',
        setup_requires=["setuptools-git-versioning"],
        scripts=[
        ],
        long_description=readme,
        classifiers=[
            'Intended Audience :: Developers',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.10',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ]
    )


if __name__ == '__main__':
    main()
