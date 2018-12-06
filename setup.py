import os, codecs, re
from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

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

repo_root = os.path.abspath(os.path.dirname(__file__))

def read(repo_root, *parts):
    with codecs.open(os.path.join(repo_root, *parts), 'r') as fp:
        return fp.read()

def find_version(repo_root, *file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name='arlib',
    version=find_version(repo_root, 'arlib', '__init__.py'),
    author='Liyu Gong',
    author_email='gongliyu@gmail.com',
    description='Common interface for archive manipulation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/gongliyu/arlib',
    packages=['arlib'],
    classifiers=classifiers)        
