User's Guide
============

.. currentmodule:: arlib

Overview
---------

*arlib* is designed using the *bridge pattern* . The abstract archive
manipulation functionality, e.g. open the archive file, query member
names, open a member, are defined in *Archive*, an *abstract base
class* called "engine". Core functionalities are defined by the
corresponding abstract methods and properties:

* :attr:`Archive.member_names`: Return a list of names of member
  files in the archive

* :meth:`Archive.open_member`: Open a member as a file object

The core functionalities are implemented in derived classes which we
call them *concrete engines*. Other functionalities may be overridden
by concrete engines but that's not required. Currently, three concrete
engines are implemented in the library:

* :class:`TarArchive`: Manipulates tar files

* :class:`ZipArchive`: Manipulates zip files

* :class:`DirArchive`: Treat a directory as an archive and files
  inside as members

Since :class:`Archive` is a *abc*, which can not be instantiate, we
implement it as a factory to produce concrete engines instead. The
design is inspired by the :mod:`pathlib`. The type of concrete engines
are automatically determined by the archive file property and the
*mode* argument to open the archive.

The function :func:`open` is a shortcut to the constructor of
:class:`Archive`.

Automatically engine selection
------------------------------

Automatically engine selection is achived by :func:`auto_engine`,
which will be called in the constructor of :class:`Archive`. Users
rarely need to call :func:`auto_engine` directly. Call the constructor
of :class:`Archive` will implicitely call :func:`auto_engine`.

:func:`auto_engine` will call an ordered list of engine determination
function (EDF) to decide the appropriate engine type. The signature of
a EDF must be :code:`edf_func(path: path-like, mode: str)`, where
:code:`path` is the path to the archive, and :code:`mode` is the mode
string to open the archive. The function should return a concrete
engine type if it can be determined, or return :code:`None` otherwise.

The EDF list already contains several EDFs. Users can extend the list
by registering new EDFs:

.. code-block:: python

   arlib.register_auto_engine(func)

A priority value can also be specified:

.. code-block:: python

   arlib.register_auto_engine(func, priority)

The value of :code:`priority` define the ordering of the registered
EDFs. The smaller the :code:`priority` value, the higher the priority
values. EDFs with higher priority will be called before EDFs with
lower priority values. The default priority value is 50.

A third bool type argument :code:`prepend` can also be specified for
:func:`register_auto_engine`. When :code:`prepend` is true, the EDF will
be put before (i.e. higher priority) other registered EDFs with the
same priority value. Otherwise, it will be put after them.

Since :func:`register_auto_engine` returns the input function object
:code:`func`, it can also be used as a non-parameterized decorator:

.. code-block:: python

   @arlib.register_auto_engine
   def func(path, mode):
       # function definition

The function :func:`register_auto_engine` also support another version of calling signature :code:`arlib.register_auto_engine(priority, prepend)`, which will return a wrapped decorator with arguments. The typical usage is:

.. code-block:: python
                
   @arlib.register_auto_engine(priority=50, prepend=False)
   def func(path, mode):
       # function definition
            

Obtain list of member names
---------------------------

The abstract property :attr:`Archive.member_names` will return a list
of :class:`str`, which represents the names of the members in the
archive:

.. code-block:: python

   ar = arlib.Archive('a.zip', 'r')
   members = ar.member_names

Concrete engines such as :class:`TarArchive` and :class:`ZipArchive`
implement the property using the underlying :mod:`zipfile` and
:mod:`tarfile` modules. :attr:`Archive.member_names` provides a
uniform interface to corresponding underlying functions.

Check member properties
---------------------------

The methods :meth:`Archive.member_is_dir` and
:meth:`Archive.member_is_file` whether the specified member is a
directory or a regular file.


Open member as a file object
----------------------------

The abstract method :meth:`Archive.open_member` provide a uniform
interface for opening member file as a file object. The signature of
the method is :code:`open_member(name, mode, **kwargs)`, where
:code:`name` is the name of member file, and :code:`mode` is the mode
argument the same as in the built-in :func:`open`
function. :code:`kwargs` are keyword arguments that will be passed to
underlying methods in :mod:`zipfile`, :mod:`tarfile` etc.


Context manager
---------------

The :class:`Archive` class also defines the context manager
functionality. Specifically, :meth:`Archive.__enter__` returns the
archive itself, and :meth:`Archive.__exit__` calls
:code:`self.close()` then return :code:`True`.


Extend the library
------------------

The architecture of the library is flexible enough to add more archive
types. Adding a new archive type includes the following steps:

#. Derive a new class and implement the core functionalities

   .. code-block:: python

      class AnotherArchive(Archive):
          def __init__(self, path, mode, **kwargs):
              # definition

          @property
          def member_names(self):
              # definition

          def open_member(self, name, mode='r', **kwargs):
              # definition

#. (optional) override methods :meth:`Archive.close`,
   :meth:`Archive.__enter__`, :meth:`Archive.__exit__` etc

#. (optional) defined and register a new EDF which could automatically
   determine the new archive type

   .. code-block:: python

      @register_auto_engine
      def another_auto_engine(path, mode):
          # definition
