#!/usr/bin/env python

from setuptools import setup

setup(
    name='prosaic',
    version='3.2.0',
    description='prose scraper & cut-up poetry generator',
    url='https://github.com/nathanielksmith/prosaic',
    author='vilmibm shaksfrpease',
    author_email='nks@lambdaphil.es',
    license='GPL',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Other Audience',
        'Topic :: Artistic Software',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
    ],
    keywords='poetry',
    packages=['prosaic'],
    install_requires = ['pymongo==2.7.2', 'nltk==3.0.0', 'numpy==1.9.0', 'sh==1.11'],
    include_package_data = True,
    entry_points = {
          'console_scripts': [
              'prosaic = prosaic.__init__:main'
          ]
    },
)
