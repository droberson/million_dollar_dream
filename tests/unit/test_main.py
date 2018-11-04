import hashlib
import os
from million_dollar_dream.bloomfilter import BloomFilter
from million_dollar_dream.main import calculate_hashes
from million_dollar_dream.main import count_files
from million_dollar_dream.main import is_md5
from million_dollar_dream.main import lookup_hashes
from million_dollar_dream.main import md5_file
from million_dollar_dream.main import md5_first_8192
from million_dollar_dream.main import readable_file
from million_dollar_dream.main import writeable_file


def test_count_files(fs):
    fake_dir = '/var/data/'
    fs.create_dir(fake_dir)
    fs.create_file(fake_dir + 'file1.txt')
    fs.create_file(fake_dir + 'file2.txt')
    fs.create_file(fake_dir + 'file3.txt')
    fake_sub_dir = '/var/data/files'
    fs.create_dir(fake_sub_dir)
    fs.create_file(fake_sub_dir + 'file4.txt')
    fs.create_file(fake_sub_dir + 'file5.txt')
    fs.create_file(fake_sub_dir + 'file6.txt')
    assert count_files(fake_dir) == 6
    assert count_files(fake_dir + 'file1.txt') == 1


def test_is_md5():
    md5_hex = hashlib.md5(b'money money money money money').hexdigest()
    assert is_md5(md5_hex)
    assert not is_md5(md5_hex[:-2])
    assert not is_md5('x' * 32)


def test_md5_first_8192(fs):
    file_path = '/var/data/xx1.txt'
    fs.create_file(file_path, contents='x' * 8193)
    full_hash = md5_file(file_path)
    assert is_md5(full_hash)
    first_8192_hash = md5_first_8192(file_path)
    assert is_md5(first_8192_hash)
    assert full_hash != first_8192_hash


def test_no_permission(fs):
    fake_dir = '/var/data/'
    file_path = fake_dir + 'xx1.txt'
    fs.create_dir(fake_dir)
    fs.create_file(file_path, contents='x' * 8193)

    assert readable_file(file_path)
    assert writeable_file(file_path)
    os.chmod(file_path, 0o111)
    assert not readable_file(file_path)
    assert not writeable_file(file_path)

    full_hash = md5_file(file_path)
    assert full_hash is None
    first_8192_hash = md5_first_8192(file_path)
    assert first_8192_hash is None


def test_calculate_and_lookup_hashes(fs):
    global bloomfilter
    bloomfilter = BloomFilter(1, 0.01)
    fake_dir = '/var/data/'
    fs.create_dir(fake_dir)
    fs.create_file(fake_dir + 'file1.txt', contents='file1')
    fs.create_file(fake_dir + 'file2.txt', contents='file2')
    fs.create_file(fake_dir + 'file3.txt', contents='file3')
    fake_sub_dir = '/var/data/files'
    fs.create_dir(fake_sub_dir)
    fs.create_file(fake_sub_dir + 'file4.txt', contents='file4')
    fs.create_file(fake_sub_dir + 'file5.txt', contents='file5')
    fs.create_file(fake_sub_dir + 'file6.txt', contents='file6')
    fake_empty_dir = '/var/data/empty'
    fs.create_dir(fake_empty_dir)

    calculate_hashes(fake_dir, bloomfilter)

    # Try a specific file, too.
    calculate_hashes(fake_dir + 'file1.txt', bloomfilter)
    os.chmod(fake_dir + 'file1.txt', 0o111)
    calculate_hashes(fake_dir + 'file1.txt', bloomfilter)

    # Make a file that isn't in the filter
    lookup_hashes(fake_dir, bloomfilter)
    fs.create_file(fake_sub_dir + 'file7.txt', contents='file7')
    lookup_hashes(fake_sub_dir + 'file7.txt', bloomfilter)
    os.chmod(fake_sub_dir + 'file7.txt', 0o111)
    lookup_hashes(fake_sub_dir + 'file7.txt', bloomfilter)
