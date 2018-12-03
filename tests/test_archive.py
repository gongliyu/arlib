import unittest, os, sys, zipfile, tarfile, tempfile
import arlib

data_path = os.path.dirname(os.path.abspath(__file__))

class AutoEngineTest(unittest.TestCase):
    def test_auto_engine(self):
        self.assertIs(
            arlib.auto_engine(os.path.join(data_path,'data/dir'), 'r'),
            arlib.DirArchive)
        self.assertIs(
            arlib.auto_engine(os.path.join(data_path,'data/tarfile.tar.gz'),
                              'r'),
            arlib.TarArchive)
        if sys.version_info[0] >= 3 and sys.version_info[1] >= 4:
            self.assertIs(
                arlib.auto_engine(
                    os.path.join(data_path,'data/tarfile.tar.xz'), 'r'),
                arlib.TarArchive)
        self.assertIs(
            arlib.auto_engine(
                os.path.join(data_path,'data/zipfile.zip'), 'r'),
            arlib.ZipArchive)
        for mode in ['w', 'x', 'a']:
            for ext in ['tar','tar.gz','tgz','tar.bz2','tar.xz']:
                self.assertIs(arlib.auto_engine('.'.join(['abc',ext]), mode),
                              arlib.TarArchive)
            self.assertIs(arlib.auto_engine('abc.zip', mode),
                          arlib.ZipArchive)

    def test_auto_engine_zip_exception(self):
        tmpdir = tempfile.gettempdir()
        fname = os.path.join(tmpdir, 'abc.zip')
        with zipfile.ZipFile(fname, 'w') as zf:
            with self.assertRaises(ValueError):
                arlib.auto_engine(zf, 'r')

        if sys.version_info[0] >= 3 and sys.version_info[1] >= 1:
            with open(fname, 'wb') as f:
                with self.assertRaises(ValueError):
                    arlib.auto_engine(f, 'r')

        if os.path.isfile(fname):
            os.remove(fname)

        fname = os.path.join(data_path, 'data/zipfile.zip')
        with zipfile.ZipFile(fname, 'r') as zf:
            with self.assertRaises(ValueError):
                arlib.auto_engine(zf, 'w')

    def test_auto_engine_tar_exception(self):
        tmpdir = tempfile.gettempdir()
        fname = os.path.join(tmpdir, 'abc.tar')
        
        with tarfile.open(fname, 'w') as tf:
            with self.assertRaises(ValueError):
                arlib.auto_engine(tf, 'r')

        if os.path.isfile(fname):
            os.remove(fname)

        fname = os.path.join(data_path, 'data/zipfile.zip')
        with zipfile.ZipFile(fname, 'r') as zf:
            with self.assertRaises(ValueError):
                arlib.auto_engine(zf, 'w')


class ArchiveTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(ArchiveTest, self).__init__(*args, **kwargs)
        
        self.tar_gz_fname = os.path.join(data_path, 'data/tarfile.tar.gz')
        self.zip_fname = os.path.join(data_path, 'data/zipfile.zip')
        self.dir_fname = os.path.join(data_path, 'data/dir')

    def _assert_member_contents(self, ar):
        with ar.open_member('a.txt') as f:
            self.assertEqual('a', f.read())
                
        with ar.open_member('b.txt') as f:
            self.assertEqual('b', f.read())

    def test_archive_tar_path(self):
        with arlib.Archive(self.tar_gz_fname) as ar:
            self.assertSequenceEqual(['a.txt', 'b.txt'], ar.member_names)
            if sys.version_info[0] >= 3:
                self._assert_member_contents(ar)
            else:
                with self.assertRaises(ValueError):
                    self._assert_member_contents(ar)
            with self.assertRaises(ValueError):
                ar.open_member('c.txt', 'w')

        with arlib.Archive(tarfile.open(self.tar_gz_fname)) as ar:
            self.assertSequenceEqual(['a.txt', 'b.txt'], ar.member_names)
            if sys.version_info[0] >= 3:
                self._assert_member_contents(ar)
            else:
                with self.assertRaises(ValueError):
                    self._assert_member_contents(ar)

    def test_archive_zip(self):
        with arlib.Archive(self.zip_fname) as ar:
            self.assertSequenceEqual(['a.txt', 'b.txt'], ar.member_names)
            self._assert_member_contents(ar)

        with arlib.Archive(zipfile.ZipFile(self.zip_fname)) as ar:
            self.assertSequenceEqual(['a.txt', 'b.txt'], ar.member_names)
            self._assert_member_contents(ar)

        if sys.version_info[0] >= 3 and sys.version_info[1] >= 1:
            with open(self.zip_fname, 'rb') as f:
                ar = arlib.Archive(f)
                self.assertSequenceEqual(['a.txt', 'b.txt'], ar.member_names)
                self._assert_member_contents(ar)
            
    def test_archive_dir(self):
        with arlib.Archive(self.dir_fname) as ar:
            self.assertSequenceEqual(['a.txt', 'b.txt'], ar.member_names)      
            self._assert_member_contents(ar)


