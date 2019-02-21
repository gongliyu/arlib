*arlib*: Common interface for archive manipulation (Tar, Zip, etc)

[![Build Status](https://travis-ci.com/gongliyu/arlib.svg?branch=master)](https://travis-ci.com/gongliyu/arlib)
[![Documentation Status](https://readthedocs.org/projects/arlib/badge/?version=latest)](https://arlib.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/gongliyu/arlib/badge.svg?branch=master)](https://coveralls.io/github/gongliyu/arlib?branch=master)
<!-- [![codecov](https://codecov.io/gh/gongliyu/arlib/branch/master/graph/badge.svg)](https://codecov.io/gh/gongliyu/arlib) -->
 
<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Installation](#installation)
  - [Install from PyPI](#install-from-pypi)
  - [Install from Anaconda](#install-from-anaconda)
- [Simple example](#simple-example)
  - [Open archive](#open-archive)
  - [List member names](#list-member-names)
  - [Open a member](#open-a-member)
  - [License](#license)
- [Documentation](#documentation)

<!-- markdown-toc end -->


## Rationale
Sometimes, we need to deal with different archive files. There are
several packages/modules for archive file manipulation, e.g.,
*zipfile* for "\*.zip" files, *tarfile* for "\*.tar.gz" or "\*.tar.bz2"
files, etc. If we want to support different archive type in our
project, probably we need to do the following:

``` python
if zipfile.is_zipfile(file):
    ar = zipfile.ZipFile(file)
    f = ar.open('member-name')
    # some processing
elif zipfile.is_tarfile(file):
    ar = tarfile.open(file)
    f = ar.extractfile('member-name')
    # some processing
else:
    # other stuffs
```

The problems of the above approach are:
* We need repeat the above code everywhere we want to support
  different archive types.
* Different archive manipulation modules (e.g. *zipfile* and
  *tarfile*) may have different API convention.

*arlib* is designed to solve the above problems. It abstracts the
logic of archive manipulations and provides a single high level
interface for users.

## Installation

### Install from PyPI

``` shell
pip install arlib
```

### Install from Anaconda

``` shell
conda install -c liyugong arlib
```

## Simple example

The abstract class *arlib.Archive* defines the common interface to
handle different archive types, such as tar file, zip file or an
directory. Three concrete classes *arlib.TarArchive*,
*arlib.ZipArchive* and *arlib.DirArchive* implement the interface
correspondingly.

### Open archive

The simplest way to open an archive is using *arlib.open* function
``` python
ar = arlib.open('abc.tar.gz', 'r')
```

This will determine the type of the archive automatically and return a
corresponding object of one of the three engine classes. If we don't
want the automatic engine determination mechanism, we can also
specify the class via argument *engine*, e.g.

``` python
ar = arlib.open('abc.tar.gz', 'r', engine=ZipArchive)
```

or we can simply construct an object of the engine class

``` python
ar = arlib.ZipArchive('abc.tar.gz', 'r')
```

### List member names

The property *member_names* will return a list of the names of members
contained in the archive, e.g.,

``` python
print(ar.member_names)
```

### Check member

Use the method *member_is_dir* and *member_is_file* to check whether a
member is a directory or a regular file

``` python
ar = arlib.open('abc.tar', 'r')
ar.member_is_dir('member_name')
ar.member_is_file('member_name')
```

### Open a member

Use the method *open_member* to open a member in the archive as a file
object

``` python
with ar.open_member('a.txt', 'r') as f:
    # do sth by using f as an opened file object
```

### Extract members to a location

Use the method *extract* to extract members to a specified location

``` python
ar = arlib.open('abc.tar', 'r')
ar.extract() # extract all the members to the current working directory
ar.extract(path='d:/hello', members=['abc.txt', 'dir1/'])
```

## License

The *arlib* package is released under the [MIT License](LICENSE)

## Documentation

https://arlib.readthedocs.io
