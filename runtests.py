import sys
import django
from django.conf import settings

settings.configure(DEBUG=True,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
        }
    },
    ROOT_URLCONF='upthor.urls',

    INSTALLED_APPS=(
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.admin',
        'upthor',
    )
)
django.setup()

if django.VERSION < (1, 8):
    from django.test.simple import DjangoTestSuiteRunner

    test_runner = DjangoTestSuiteRunner(verbosity=1)
else:
    from django.test.runner import DiscoverRunner

    test_runner = DiscoverRunner(verbosity=1)

failures = test_runner.run_tests(['upthor', ])

if failures:
    sys.exit(failures)
