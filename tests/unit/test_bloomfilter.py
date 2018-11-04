import os
from million_dollar_dream.bloomfilter import BloomFilter
from million_dollar_dream.main import md5_file


def test_accuracy():
    items = 1000
    false_positive_rate = 0.1
    bloom_filter = BloomFilter(items, false_positive_rate)
    size = bloom_filter.size
    hashcount = bloom_filter.hashcount
    expected_accuracy = float(100 - (100 * false_positive_rate))
    accuracy = round(bloom_filter.accuracy(size, hashcount, items), 0)
    assert accuracy == expected_accuracy


def test_add_and_lookup(fs):
    items = 5
    false_positive_rate = 0.1
    bloom_filter = BloomFilter(items, false_positive_rate)
    file_path_1 = '/var/data/xx1.txt'
    file_path_2 = '/var/data/xx2.txt'
    fs.create_file(file_path_1, contents='file1')
    fs.create_file(file_path_2, contents='file2')
    assert os.path.exists(file_path_1)
    assert os.path.exists(file_path_2)
    md5_file_1 = md5_file(file_path_1)
    md5_file_2 = md5_file(file_path_2)

    assert not bloom_filter.lookup(md5_file_1)
    assert not bloom_filter.lookup(md5_file_2)

    bloom_filter.add(md5_file_1)
    assert bloom_filter.lookup(md5_file_1)
    assert not bloom_filter.lookup(md5_file_2)


def test_expected_sizes():
    expected_items = 3
    false_positive_rate = 0.01
    expected_ideal_hashcount = 6
    expected_size = 28
    expected_bytesize = 4
    expected_bytesize_human = '4.0bytes'
    bloom_filter = BloomFilter(expected_items, false_positive_rate)
    assert bloom_filter.hashcount == expected_ideal_hashcount
    assert bloom_filter.size == expected_size
    assert bloom_filter.bytesize == expected_bytesize
    assert bloom_filter.bytesize_human == expected_bytesize_human

    expected_items = 1709
    bloom_filter = BloomFilter(expected_items, false_positive_rate)
    expected_bytesize_human = '2.0Kb'
    assert bloom_filter.bytesize_human == expected_bytesize_human


def test_save_and_load(fs):
    expected_items = 3
    false_positive_rate = 0.01
    expected_size = 28
    fake_dir = '/var/data/'
    fake_path = fake_dir + 'test_filter'
    fs.create_dir(fake_dir)
    bloom_filter = BloomFilter(expected_items, false_positive_rate)
    assert bloom_filter.size == expected_size
    bloom_filter.save(fake_path)

    new_expected_items = 5
    new_false_positive_rate = 0.02
    new_expected_size = 40
    new_bloom_filter = BloomFilter(new_expected_items, new_false_positive_rate)
    assert new_bloom_filter.size == new_expected_size

    # Should be size of original filter
    new_bloom_filter.load(fake_path)
    assert new_bloom_filter.size == expected_size


