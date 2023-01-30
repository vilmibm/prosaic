#!/usr/bin/env python

from setuptools import setup

setup(
    name='prosaic',
    version='6.1.1',
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
    install_requires = ['nltk==3.8.1',
                        'numpy==1.24.0',
                        'SQLAlchemy==1.4.46',
                        'pyhocon==0.3.29',
                        'psycopg2-binary==2.9.5',],
    include_package_data = True,
    entry_points = {
          'console_scripts': [
              'prosaic = prosaic.__init__:main'
          ]
    },
)
