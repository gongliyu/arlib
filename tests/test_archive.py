# -*- coding: utf-8 -*-

import uuid
import unittest, os, sys, zipfile, tarfile, tempfile, pytest
import shutil
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


def test_auto_engine_error():
    dst = tempfile.mkdtemp()
    
    with zipfile.ZipFile(os.path.join(dst, 'abc.zip'), 'w') as f:
        with pytest.raises(Exception):
            arlib.auto_engine(f, 'r')
    with open(os.path.join(dst, 'abc.zip'), 'wb') as f:
        if sys.version_info[0] >= 3 and sys.version_info[1] >= 1:
            with pytest.raises(Exception):
                arlib.auto_engine(f, 'r')
    with zipfile.ZipFile(os.path.join(data_path, 'zipfile.zip'), 'r') as f:
        with pytest.raises(Exception):
            arlib.auto_engine(f, 'w')
    with zipfile.ZipFile(os.path.join(dst, 'abc.zip'), 'w') as f:
        assert arlib.auto_engine(f, 'w') is arlib.ZipArchive
    shutil.rmtree(dst)

def test_open_error():
    dst = tempfile.mkdtemp()
    with tarfile.open(os.path.join(dst, 'abc.tar'), 'w') as f:
        with pytest.raises(Exception):
            arlib.auto_engine(f, 'r')
    with pytest.raises(Exception):
        arlib.open(str(uuid.uuid4())+'.txt', 'r')
    with pytest.raises(Exception):
        arlib.open(str(uuid.uuid4())+'.txt', 'r', engine=str)
    shutil.rmtree(dst)    
    

@pytest.mark.parametrize('fname, mode', [
    (zipfile.ZipFile(os.path.join(data_path, 'zipfile.zip')), 'w'),
    (tarfile.open(os.path.join(data_path, 'tarfile.tar.gz')), 'w'),
    ])
def test_auto_engine_exception(fname, mode):
    with pytest.raises(Exception):
        arlib.auto_engine(fname, mode)


def test_validate_member_name_error():
    with arlib.open(os.path.join(data_path, 'member_check.zip')) as ar:
        with pytest.raises(Exception):
            ar.validate_member_name(str(uuid.uuid4()))

@pytest.mark.parametrize('fname, member', [
    ('member_check', 'dir'),
    ('member_check.zip', 'dir/'),
    ('member_check.tar', 'dir'),
    ])
def test_open_dir_member(fname, member):
    with arlib.open(os.path.join(data_path, fname)) as ar:
        with pytest.raises(Exception):
            ar.open_member(member, mode='r')
        
        
@pytest.mark.parametrize('fname',[
    'member_check',
    'member_check.zip',
    'member_check.tar'
    ])
def test_member_check(fname):
    with arlib.open(os.path.join(data_path, fname)) as ar:
        assert ar.member_is_dir('dir')
        assert ar.member_is_file('a.txt')


@pytest.mark.parametrize('fname, members',[
    ('member_check', None),
    ('member_check', ['dir']),
    ('member_check', ['dir', 'a.txt']),
    ('member_check', ['dir', 'dir/b.txt']),
    ('member_check', ['dir/b.txt', 'dir/']),
    ('member_check.tar', None),
    ('member_check.tar', ['dir']),
    ('member_check.tar', ['dir', 'a.txt']),
    ('member_check.tar', ['dir', 'dir/b.txt']),
    ('member_check.zip', None),
    ('member_check.zip', ['dir']),
    ('member_check.zip', ['dir', 'a.txt']),
    ('member_check.zip', ['dir', 'dir/b.txt']),
    ('member_check.zip', ['dir/b.txt', 'dir/']),    
    ])
def test_extract(fname, members):
    dst = tempfile.mkdtemp()
    with arlib.open(os.path.join(data_path, fname)) as ar1:
        ar1.extract(dst, members)
        with arlib.open(dst) as ar2:
            if members is not None:
                names = [ar1.validate_member_name(x) for x in members]
            else:
                names = ar1.member_names
            assert set(names) == set(ar2.member_names)
            for name in names:
                if ar1.member_is_file(name):
                    assert ar1.open_member(name,'rb').read() == ar2.open_member(name, 'rb').read()
    shutil.rmtree(dst)
                

def test_tar_archive_fileobj():
    with open(os.path.join(data_path, 'tarfile.tar.gz'), 'rb') as f:
        with arlib.TarArchive(f) as ar:
            assert set(ar.member_names) == set(['a.txt', 'b.txt'])
    with open(os.path.join(data_path, 'zipfile.zip'), 'rb') as f:
        with pytest.raises(Exception):
            arlib.TarArchive(f)
    
