#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
<<<<<<< HEAD
# Copyright (C) 2011-2015 Star2Billing S.L.
=======
# Copyright (C) 2011-2014 Star2Billing S.L.
>>>>>>> 3da8460... Merge branch 'release/v2.15.0'
#
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#

<<<<<<< HEAD
# IMPORT SETTINGS
# ===============
=======
#IMPORT SETTINGS
#===============
>>>>>>> 3da8460... Merge branch 'release/v2.15.0'
from settings import *
import os

APPLICATION_DIR = os.path.dirname(globals()['__file__']) + '/../'

# Build faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': ':memory:',
        'TEST': {'NAME': APPLICATION_DIR + '/database/test-newfies.db'},
    }
}

BROKER_BACKEND = "memory"
CELERY_ALWAYS_EAGER = True

SOUTH_TESTS_MIGRATE = False

# INSTALLED_APPS += ('django_nose', )
# TEST_RUNNER = 'django_nose.run_tests'
