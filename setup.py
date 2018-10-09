#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup, find_packages


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='tox-lambda-autodiscovery',
    description='autodiscovery and autocreate tox testenv to aws lambda function',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    version='0.1.0',
    author='Fabio C. Barrionuevo da Luz',
    author_email='bnafta@gmail.com',
    maintainer='Fabio C. Barrionuevo da Luz',
    maintainer_email='bnafta@gmail.com',
    url='https://github.com/luzfcb/tox-lambda-autodiscovery',
    packages=find_packages(),
    python_requires='>=3.6, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    install_requires=['tox>=3.3.0'],
    entry_points={'tox': ['lambda-autodiscovery = tox_lambda_autodiscovery.plugin']},
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: tox',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
)
