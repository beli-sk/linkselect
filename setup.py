#!/usr/bin/env python
from setuptools import setup, find_packages
from codecs import open # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# get version number
defs = {}
with open(path.join(here, 'src/linkselect/defs.py')) as f:
    exec(f.read(), defs)

setup(
    name='linkselect',
    version=defs['__version__'],
    description=defs['app_description'],
    long_description=long_description,
    #url='',
    author="Michal Belica",
    author_email="devel@beli.sk",
    license="GPL-3",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
        ],
    zip_safe=True,
    package_dir={'': 'src'},
    packages=['linkselect'],
    entry_points={
        'gui_scripts': [
            'linkselect = linkselect.gui:main',
            ],
        },
    )

