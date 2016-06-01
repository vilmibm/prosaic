#!/usr/bin/env python

from setuptools import setup

setup(
    name='prosaic',
    version='4.0.0',
    description='prose scraper & cut-up poetry generator',
    url='https://github.com/nathanielksmith/prosaic',
    author='vilmibm shaksfrpease',
    author_email='nks@lambdaphil.es',
    license='GPL',
    classifiers=[
        'Topic :: Artistic Software',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
    keywords='poetry',
    packages=['prosaic'],
    install_requires = ['nltk==3.0.5',
                        'numpy==1.9.0',
                        'SQLAlchemy==1.0.12',
                        'pyhocon==0.3.29',
                        'psycopg2==2.6.1',],
    include_package_data = True,
    entry_points = {
          'console_scripts': [
              'prosaic = prosaic.__init__:main'
          ]
    },
)
