import unittest, os, sys, zipfile, tarfile, tempfile, pytest
import arlib

data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

@pytest.mark.parametrize('fname', [
    os.path.join(data_path, 'tarfile.tar.gz'),
    os.path.join(data_path, 'tarfile.tar.xz'),
    os.path.join(data_path, 'zipfile.zip'),
    os.path.join(data_path, 'dir'),
    tarfile.open(os.path.join(data_path, 'tarfile.tar.gz')),
    zipfile.ZipFile(os.path.join(data_path, 'zipfile.zip')),
    open(os.path.join(data_path, 'zipfile.zip'), 'rb'),
    ])
def test_arlib_read(fname):
    if sys.version_info[0] >= 3:
        with arlib.open(fname, 'r') as ar:
            assert ar.member_names == ['a.txt', 'b.txt']
            with ar.open_member('a.txt', 'r') as f:
                assert f.read() == 'a'
            with ar.open_member('b.txt', 'r') as f:
                assert f.read() == 'b'
    
@pytest.mark.parametrize('fname, mode, res', [
    ('x.zip', 'w', arlib.ZipArchive),
    ('x.tar.gz', 'w', arlib.TarArchive),
    ])
def test_auto_engine(fname, mode, res):
    assert arlib.auto_engine(fname, mode) is res


@pytest.mark.parametrize('fname, mode', [
    (zipfile.ZipFile(os.path.join(data_path, 'zipfile.zip')), 'w'),
    (tarfile.open(os.path.join(data_path, 'tarfile.tar.gz')), 'w'),
    ])
def test_auto_engine_exception(fname, mode):
    with pytest.raises(Exception):
        arlib.auto_engine(fname, mode)

