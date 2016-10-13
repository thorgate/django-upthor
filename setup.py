import os
from setuptools import setup, find_packages


from upthor import __version__ as version

try:
    from pypandoc import convert

    def read_md(f):
        return convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")

    def read_md(f):
        return open(f, 'r', encoding='utf-8').read()

setup(
    name='django-upthor',
    version=version,
    description='django-upthor provides a django application for simple ajax file uploads.',
    long_description=read_md('README.md'),
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
