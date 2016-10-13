import os
from setuptools import setup, find_packages

from upthor import __version__ as version

f = open(os.path.join(os.path.dirname(__file__), 'README.md'))
readme = f.read()
f.close()

setup(
    name='django-upthor',
    version=version,
    description='`django-upthor` provides a django application for simple ajax file uploads.',
    long_description=readme,
    author="Thorgate",
    author_email='info@thorgate.eu',
    url='https://github.com/thorgate/django-upthor',
    packages=find_packages(),
    package_data={'upthor': [
        'static/upthor/css/*',
        'static/upthor/fonts/*',
        'static/upthor/js/*',
    ]},
    include_package_data=True,
    install_requires=[
        'Django',
        'Pillow',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
)
