#!/usr/bin/env python

#
# Usage : python manage.py test --with-xtraceback --with-color
# Run on shell test coverage : python manage.py test --progressive-with-bar --with-coverage --cover-html --cover-package=newfies
#
#

import sys
import logging
from optparse import OptionParser
from coverage import coverage
import settings

#from tests.config import configure

logging.disable(logging.CRITICAL)


import os
from django.utils.importlib import import_module


PINAX_ROOT = os.path.abspath(os.path.dirname(newfies.__file__))

def setup_environ(dunder_file=None, project_path=None, relative_project_path=None, settings_path=None):
    assert not (dunder_file and project_path), ("You must not specify both "
        "__file__ and project_path")

    if dunder_file is not None:
        file_path = os.path.abspath(os.path.dirname(dunder_file))
        if relative_project_path is not None:
            project_path = os.path.abspath(os.path.join(file_path, *relative_project_path))
        else:
            project_path = file_path

    # the basename must be the project name and importable.
    project_name = os.path.basename(project_path)

    # setup Django correctly (the hard-coding of settings is only temporary.
    # carljm's proposal will remove that)
    if settings_path is None:
        if "DJANGO_SETTINGS_MODULE" not in os.environ:
            os.environ["DJANGO_SETTINGS_MODULE"] = "%s.settings" % project_name
    else:
        os.environ["DJANGO_SETTINGS_MODULE"] = settings_path

    # ensure the importablity of project
    sys.path.append(os.path.join(project_path, os.pardir))
    import_module(project_name)
    sys.path.pop()

    # Pinax adds an app directory for users as a reliable location for
    # Django apps
    sys.path.insert(0, os.path.join(project_path, "newfies"))


def run_tests(options, *test_args):
    from django_nose import NoseTestSuiteRunner
    test_runner = NoseTestSuiteRunner(verbosity=options.verbosity,
                                      pdb=options.pdb,
                                      )
    if not test_args:
        test_args = ['tests']
    num_failures = test_runner.run_tests(test_args)
    if num_failures:
        sys.exit(num_failures)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-c', '--coverage', dest='use_coverage', default=False,
                      action='store_true', help="Generate coverage report")
    parser.add_option('-v', '--verbosity', dest='verbosity', default=1,
                      type='int', help="Verbosity of output")
    parser.add_option('-d', '--pdb', dest='pdb', default=False,
                      action='store_true', help="Whether to drop into PDB on failure/error")
    (options, args) = parser.parse_args()

    # If no args, then use 'progressive' plugin to keep the screen real estate
    # used down to a minimum.  Otherwise, use the spec plugin
    nose_args = ['-s', '-x',
                 '--with-progressive' if not args else '--with-spec']
    #configure(nose_args)


    project_path = os.path.join(PINAX_ROOT, "projects", name)
    setup_environ()

    if options.use_coverage:
        print 'Running tests with coverage'
        c = coverage(source=['newfies'])
        c.start()
        run_tests(options, *args)
        c.stop()
        print 'Generate HTML reports'
        c.html_report()
    else:
        run_tests(options, *args)
