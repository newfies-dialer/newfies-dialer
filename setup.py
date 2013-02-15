#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2013 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

from setuptools import setup, find_packages
import os
import re
import newfies


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

README = read('README.rst')


def parse_requirements(file_name):
    requirements = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'(\s*#)|(\s*$)', line):
            continue
        if re.match(r'\s*-e\s+', line):
            requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
        elif re.match(r'(\s*git)|(\s*hg)', line):
            pass
        else:
            requirements.append(line)
    return requirements


def parse_dependency_links(file_name):
    dependency_links = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'\s*-[ef]\s+', line):
            dependency_links.append(re.sub(r'\s*-[ef]\s+', '', line))

    return dependency_links


setup(
    name='newfies-dialer',
    version=newfies.__version__,
    description='Newfies is a Bulk Dialer and Voice Broadcasting application '
                'dedicated to provide information via phone technology.',
    long_description=read('README.rst'),
    author='Belaid Arezqui',
    author_email='areski@gmail.com',
    url='http://www.newfies-dialer.org/',
    include_package_data=True,
    zip_safe=False,
    package_dir={'newfies': 'newfies'},
    packages=find_packages(),
    package_data={},
    install_requires=parse_requirements('install/requirements/all-requirements.txt'),
    dependency_links=parse_dependency_links('install/requirements/all-requirements.txt'),
    license='MPL 2.0 License',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers, Users',
        'License :: OSI Approved :: MPL 2.0 License',
        'Operating System :: OS Independent',
        'Programming Language :: Python, Javascript, HTML',
        'Topic :: Software Development'
    ],
)
