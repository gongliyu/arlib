import os
from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'VERSION')) as f:
    version = f.read().strip()

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: PyPy'
    ]

setup(
    name='arlib',
    version=version,
    author='Liyu Gong',
    author_email='gongliyu@gmail.com',
    description='Common interface for archive manipulation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/gongliyu/arlib',
    include_package_data=True,
    packages=['arlib'],
    classifiers=classifiers)        
