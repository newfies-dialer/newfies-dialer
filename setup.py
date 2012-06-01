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
# Copyright (C) 2011-2012 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

import os
from setuptools import setup, find_packages
from setuptools.dist import Distribution
import pkg_resources
import sys
import re
from newfies import VERSION

add_django_dependency = True
try:
    pkg_resources.get_distribution('Django')
    add_django_dependency = False
except pkg_resources.DistributionNotFound:
    try:
        import django
        if django.VERSION[0] >= 1 and django.VERSION[1] >= 2 \
            and django.VERSION[2] >= 0:
            add_django_dependency = False
    except ImportError:
        pass

Distribution({'setup_requires': add_django_dependency
             and ['Django >=1.3.0'] or []})

COMMANDS = {}
try:
    from sphinx.setup_command import BuildDoc
    COMMANDS['build_sphinx'] = BuildDoc
except ImportError:
    pass
try:
    from sphinx_pypi_upload import UploadDoc
    COMMANDS['upload_sphinx'] = UploadDoc
except ImportError:
    pass

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.

(packages, data_files, temp_data_files, addons_data_files) = ([], [],
        [], [])
(docs_data_files, resources_data_files) = ([], [])

root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)


def parse_requirements(file_name):
    requirements = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'(\s*#)|(\s*$)', line):
            continue
        if re.match(r'\s*-e\s+', line):
            requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1',
                                line))
        elif re.match(r'(\s*git)|(\s*hg)', line):
            pass
        else:
            requirements.append(line)
    return requirements


def parse_dependency_links(file_name, install_flag=False):
    dependency_links = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'\s*-e\s+', line):
            dependency_links.append(re.sub(r'\s*-e\s+', '', line))
        if re.match(r'(\s*git)|(\s*hg)', line):
            if install_flag == True:
                line_arr = line.split('/')
                line_arr_length = len(line.split('/'))
                pck_name = line_arr[line_arr_length - 1].split('.git')
                if len(pck_name) == 2:
                    os.system('pip install -f %s %s' % (pck_name[0],
                              line))
                if len(pck_name) == 1:
                    os.system('pip install -f %s %s' % (pck_name, line))
    return dependency_links


install_flag = False
if sys.argv[1] == 'install':
    install_flag = True

setup(
    name='newfies-dialer',
    version=VERSION.replace(' ', '-'),
    description='Newfies is a Bulk Dialer and Voice Broadcasting application '
                'dedicated to provide information via phone technology.',
    long_description=open('README.rst').read(),
    author='Belaid Arezqui',
    author_email='areski@gmail.com',
    url='http://www.newfies-dialer.org/',
    download_url='https://github.com/Star2Billing/newfies-dialer'
                '/tarball/master',
    packages=find_packages(),
    include_package_data=True,
    license='MPL 2.0 License',
    classifiers=[
        'Development Status :: 1 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers, Users',
        'License :: OSI Approved :: MPL 2.0 License',
        'Operating System :: OS Independent',
        'Programming Language :: Python, Javascript, HTML',
        'Topic :: Voice Broadcast Software',
        ],
    zip_safe=False,
    install_requires=parse_requirements('install/conf/requirements.txt'),
    dependency_links=parse_dependency_links('install/conf/requirements.txt',
        install_flag),
    setup_requires=['Django >= 1.3.0', 'Sphinx >= 0.4.2'],
    cmdclass=COMMANDS,
    )
