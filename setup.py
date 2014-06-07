#!/usr/bin/env python

from setuptools import setup

setup(
    name='prosaic',
    version='1.0.0b1',
    description='prose scraper & cut-up poetry generator',
    url='https://github.com/nathanielksmith/prosaic',
    author='vilmibm shaksfrpease',
    author_email='nks@lambdaphil.es',
    license='GPL',
    classifiers=[
        'Development Status :: 4',
        'Intended Audience :: Poets',
        'Topic :: Poetry',
        'License :: OSI Approved :: GPL License',
        'Programming Language :: Hy',
    ],
    keywords='poetry',
    packages=['prosaic'],
    install_requires = ['pymongo', 'hy', 'nltk'],
    package_data=[('prosaic', ['nltk_data'])],
    # TODO entry points
)
