# -*- coding: utf-8 -*-

import tarfile
import zipfile
import io
import os
import collections
import bisect
import abc
import fnmatch
import sys

import decoutils

if sys.version_info[0] == 2:
    import __builtin__ as builtins
else:
    import builtins
    
__version__ = '0.0.4'

_auto_engine = []

if sys.version_info[0] >= 3 and sys.version_info[1] >= 6:
    _path_classes = (str, bytes, os.PathLike)
else:
    _path_classes = (str, bytes)


@decoutils.decorator_with_args
def register_auto_engine(func, priority=50, prepend=False):
    """Register automatic engine determing function
    
    Two possible signatures:

      * :code:`register_auto_engine(func, priority=50, prepend=False)`
      * :code:`register_auto-engine(priority=50, prepend=False)`

    The first one can be used as a regular function as well as a
    decorator. The second one is a decorator with arguments

    Args:

      func (callable): A callable which determines archive engine from
        file properties and open mode. The signature should be:
        func(path, mode) where path is a file-like or path-like
        object, and mode str to open the file.

      priority (int, float): Priority of the func, small number means
        higher priority. When multiple functions are registered by
        multiple call of register_auto_engine, functions will be used
        in an ordering determined by thier priortities. Default to 50.

      prepend (bool): If there is already a function with the same
        priority registered, insert to the left (before) or right
        (after) of it. Default to False.

    Return:

      The first version of signature will return the input callable
      :code:`func`, therefore it can be used as a decorator (without
      arguments). The second version will return a decorator wrap.

    """
    p = [x[0] for x in _auto_engine]
    if prepend:
        i = bisect.bisect_left(p, priority)
    else:
        i = bisect.bisect_right(p, priority)
    _auto_engine.insert(i, (priority, func))


@register_auto_engine
def auto_engine_zip(path, mode):
    if 'r' in mode:
        if isinstance(path, zipfile.ZipFile):
            if path.mode != 'r':
                raise ValueError('Mode of ZipFile object is not compatible'
                                 ' with the mode argument.')
            return ZipArchive
        
        if (sys.version_info[0] >= 3 and sys.version_info[1] >= 1 and
            isinstance(path, io.IOBase) and 'b' in path.mode):
            if not path.readable():
                raise ValueError('Opened file is not readable, but the mode'
                                 'argument is '+mode)
            if zipfile.is_zipfile(path):
                return ZipArchive
            
        if isinstance(path, _path_classes):
            if os.path.isfile(path) and zipfile.is_zipfile(path):
                return ZipArchive
    else:
        if isinstance(path, zipfile.ZipFile):
            if path.mode not in ['a', 'w', 'x']:
                raise ValueError('Mode of ZipFile object is not compatible'
                                 ' with the mode argument.')
            return ZipArchive
            
        if isinstance(path, _path_classes):
            if fnmatch.fnmatch(path, '*.zip'):
                return ZipArchive
    return None

@register_auto_engine
def auto_engine_tar(path, mode):
    if 'r' in mode:
        if isinstance(path, tarfile.TarFile):
            if path.mode != 'r':
                raise ValueError('Mode of TarFile object is not compatible'
                                 ' with the mode argument.')
            return TarArchive
        
        if isinstance(path, _path_classes):
            path = os.path.abspath(path)
            if os.path.isfile(path) and tarfile.is_tarfile(path):
                return TarArchive
    else:
        if isinstance(path, tarfile.TarFile):
            if path.mode not in ['a', 'w', 'x']:
                raise ValueError('Mode of TarFile object is not compatible'
                                 ' with the mode argument.')
            return TarArchive
        
        if isinstance(path, _path_classes):
            if any(fnmatch.fnmatch(path, x) for x in
                   ['*.tar', '*.tgz', '*.tar.gz', '*.tar.bz2', '*.tar.xz']):
                return TarArchive
    return None

@register_auto_engine
def auto_engine_dir(path, mode):
    if 'r' in mode:
        if isinstance(path, _path_classes):
            if os.path.isdir(path):
                return DirArchive
    return None

def auto_engine(path, mode='r'):
    """Automatically determine engine type from file properties and file
    mode using the registered determining functions

    Args:

      path (file-like, path-like): Opened file object or path to the
        archive file

      mode (str): Mode str to open the file. Default to "r".

    Return:

      type, NoneType: a subclass of Archive if successfully find one
        engine, otherwise None

    See also:

      :func:`is_archive`

    """
    for _, func in _auto_engine:
        engine = func(path, mode)
        if engine is not None:
            break
    return engine

def is_archive(path, mode='r'):
    """Determine if the file specified by :code:`path` is a valid archive
    when opened with :code:`mode`

    Basically, the function checks the result of :func:`auto_engien`,
    and return :code:`True` if the result is not None, and return
    :code:`False` otherwise.

    Args:
    
      path (file-like, path-like): Opened file object or path to the
        archive file.

      mode (str): Mode str to open the file. Default to "r".

    Return:

      bool: :code:`True` if the path is valid archive, :code:`False`
    otherwise.

    Examples:

      >>> is_archive('a.tar.gz', 'w')
      True
      >>> is_archive('a.tar.bz2', 'w')
      True
      >>> is_archive('a.txt', 'w')
      False

    See also:

      :func:`auto_engine`

    """
    return auto_engine(path, mode) is not None
    

def assert_is_archive(path, mode):
    """Assert that :code:`path` can be opened as a valid archive with
    :code:`mode`

    Args:
    
      path (file-like, path-like): Opened file object or path to the
        archive file.

      mode (str): Mode str to open the file. Default to "r".
    
    Examples:
    
      >>> assert_is_archive('a.tar.gz', 'w')
      >>> assert_is_archive('a.txt', 'w')
      Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
      ValueError: a.txt cannot be opened as a valid archive with w

    See also:

      :func:`is_archive`

    """
    if not is_archive(path, mode):
        raise ValueError(str(path)+' cannot be opened as a valid archive '
                         'with '+mode)

class Archive:

    """Common-interface to different type of archive files manipulation
    
    Args:

      path (path-like, file-like): Path of the archive to read or write

      mode (str): The mode to open the member, same as in
        :func:`open`. Default to 'r'.
      
      engine (type): Class object of a specific subclass Archive which
        implements the logic of processing a specific type of
        Archive. Provided implements:

        * ZipArchive: zip file archive using the `zipfile` module
    
        * TarArchive: tar file archive using the `tarfile` module

        * DirArchive: directory as an archive using the `pathlib` module

        * None: Automatically determine engines by file properties and
          mode

      \**kwargs : Additional keyword arguments passed to the underlying
        engine constructor

    Note:

      The constructor of a concrete engine should take at least one
      positional argument `path` and one optional argument `mode` with
      default value to `r`.

    """
    __metaclass__ = abc.ABCMeta
    def __new__(cls, path, mode='r', engine=None, **kwargs):
        if cls is not Archive:
            return object.__new__(cls)

        if engine is None:
            engine = auto_engine(path, mode)
            if engine is None:
                raise RuntimeError('Cannot automatically determine engine.')
        if not issubclass(engine, Archive):
            raise TypeError('engine must be a subclass of Archive, received:'
                            ' '+str(engine))
        return engine.__new__(engine, path, mode, **kwargs)

    @property
    @abc.abstractmethod
    def member_names(self):
        """Get list of names of the members (i.e. files contained in the
        archive)

        Return:

          list[str]: list of member names
        """
        pass

    @abc.abstractmethod
    def open_member(self, name, mode='r', **kwargs):
        """Open a member file contained in the archive

        Args:

          name (str): name of the member file to open

          mode (str): The mode to open the member, same as in
            :func:`open`. Default to 'r'.

          \**kwargs: Additional keyword arguments that will be passed
            to the underlying function.

        Return:

          file-like: A opened file object associated with the member
          file

        """
        pass

    def close(self):
        """Release resources such as closing files etc
        """
        pass

    def __enter__(self):
        """Context manager enter function

        Return:

          Archive: The archive object itself
        """
        return self

    def __exit__(self, type, value, traceback):
        """Context manager exit function

        Call self.close() then return True
        """
        self.close()
        
        
class TarArchive(Archive):
    """Archive engine for *tar* files using the `tarfile` module

    Args:

      path (path-like): Path to the archive

      mode (str): The mode to open the member, same as in
        :func:`open`.

      \**kwargs : Other keyword arguments that will be passed to the
        underlying function.

    """
    def __init__(self, path, mode='r', **kwargs):
        self._need_close = True
        if isinstance(path, tarfile.TarFile):
            self._file = path
            self._need_close = False
        else:
            self._file = tarfile.open(path, mode=mode, **kwargs)

    @property
    def member_names(self):
        names = self._file.getnames()
        return names


    def open_member(self, name, mode='r'):
        """Open member file contained in the tar archive

        Args:

          name (str): Name of the member to open

          mode (str): The mode argument to open. Same as in :func:`open`.

        Return:

          file-like: The opened file object associated with the member
          file.

        Note:

          Members of tar archive cannot be opened in write mode.
        """
        mode = mode.lower()
        if 'r' not in mode:
            raise ValueError('members of tar archive can not be opened in'
                             ' write mode')
        f = self._file.extractfile(name)
        if 'b' not in mode:
            if sys.version_info[0] >= 3:
                f = io.TextIOWrapper(f)
            else:
                raise ValueError('I do not know how to wrap binary file object'
                                 ' to text io.')
        return f

    def close(self):
        if self._need_close:
            self._file.close()


class ZipArchive(Archive):
    """Archive engine for *zip* files using the `zipfile` module
    """

    def __init__(self, path, *args, **kwargs):
        self._need_close = True
        if isinstance(path, zipfile.ZipFile):
            self._file = path
            self._need_close = False
        else:
            self._file = zipfile.ZipFile(path, *args, **kwargs)

    @property
    def member_names(self):
        names = self._file.namelist()
        return names


    def open_member(self, name, mode='r', **kwargs):
        """Open a member file in the zip archive

        Args:

          name (str): Name of the member file

          mode (str): The mode argument to open. Same as in :func:`open`.

          \**kwargs: Additional keyword arguments that will be passed
            to :func:`zipfile.ZipFile.open`

        
        Return:

          file-like: The opened file object associated with the member
          file.
        """
        f = self._file.open(name, mode)
        if 'b' not in mode:
            f = io.TextIOWrapper(f)
        return f

    def close(self):
        if self._need_close:
            self._file.close()


class DirArchive(Archive):
    """Archive engine that treat a directory as an archive using `pathlib`
    module
    """
    def __init__(self, path, mode='r'):
        self._file = os.path.abspath(path)
        

    @property
    def member_names(self):
        return os.listdir(self._file)

    def open_member(self, name, mode='r', **kwargs):
        """Open a member in the directory

        Args:

          name (str): Name of the member file

          mode (str): The mode argument to open. Same as in :func:`open`.

          \**kwargs: Additional keyword arguments that will be passed
            to :func:`open`
        
        Return:

          file-like: The opened file object associated with the member
          file.

        """
        path = os.path.join(self._file, name)
        return builtins.open(path, mode, **kwargs)


def open(*args, **kwargs):
    """Shortcut to constructor of :class:`Archive`
    """
    return Archive(*args, **kwargs)
