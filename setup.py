# SPDX-FileCopyrightText: 2023 Robert Bosch GmbH
#
# SPDX-License-Identifier: Apache-2.0

import os
from setuptools import setup, find_namespace_packages


__INSTALL_REQUIRES__ = [
    'PyYAML',
]

__CONSOLE_SCRIPTS__ = [
]


__NAME__            = 'action.toolkit'
__VERSION__         = os.getenv('PACKAGE_VERSION', 'none')
__URL__             = 'https://github.com/boschglobal/action.toolkit.git'
__LICENSE__         = 'Apache-2.0'
__AUTHOR__          = 'Timothy Rule'
__AUTHOR_EMAIL__    = 'Timothy.Rule@de.bosch.com'
__PYTHON_MIN_VER__  = '3.8'
__NAMESPACE__       = 'action'
__KEYWORDS__        = ('github', 'action')
__DESCRIPTION__     = 'GitHub Action Python Toolkit'

__DESCRIPTION_LONG__ = """
GitHub Action Python Toolkit
============================

GitHub Action Python Toolkit for implementing Python based GitHub Actions.

"""


setup(
    name = __NAME__,
    version = __VERSION__,
    author = __AUTHOR__,
    author_email = __AUTHOR_EMAIL__,
    license = __LICENSE__,
    description = __DESCRIPTION__,
    long_description = __DESCRIPTION_LONG__,
    long_description_content_type = 'text/markdown',
    url = __URL__,
    keywords = ' '.join(__KEYWORDS__),
    packages = find_namespace_packages(include=[f'{__NAMESPACE__}.*']),
    python_requires = f'>={__PYTHON_MIN_VER__}',
    install_requires = __INSTALL_REQUIRES__,
    setup_requires = [],
    include_package_data = True,
    zip_safe = False,
    entry_points = {
        'console_scripts' : __CONSOLE_SCRIPTS__,
    },
    classifiers=[
        f'License :: {__LICENSE__}',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        f'Programming Language :: Python :: {__PYTHON_MIN_VER__}',
    ],
)
