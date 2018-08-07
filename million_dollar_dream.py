#!/usr/bin/env python3

"""
This tool will create and compare bloom filters containing file hashes. It
will be useful to see which files are new or have changed on a host, provided
a filter has been pre-calculated.

Example:
    ./million_dollar_dream.py calculate ubuntu-16.04.filter /bin /sbin /etc /usr
    ./million_dollar_dream.py lookup ubuntu-16.04.filter /bin/bash
    ...
    This will show what is/isnt in the filter
    ...

TODO:
    - Test on big endian machine
	- virusshare filter
	- NIST filter
	- Create filter from list of hashes
	- Make as many filters as possible for likely software
        - Ubuntu distros
        - Debian distros
        - CentOS distros
	- Test on Windows?
	- Test on python2.7
        - to_bytes and from_bytes do not work.
"""

import os
import sys
import hashlib

from bloomfilter import BloomFilter


def md5_first_8192(filename):
    """md5_first_8192() - Calculates MD5 of first 8kb of a file for great speed.

    Args:
        filename (str) - Path to file.

    Returns:
        Hexadecimal string of the hash on success.
        None if the hash couldn't be calculated.
    """
    md5hash = hashlib.md5()

    try:
        with open(filename, "rb") as filep:
            md5hash.update(filep.read(8192))
    except PermissionError:
        return None
    return md5hash.hexdigest()


def md5_file(filename):
    """md5_file() - Calculates MD5 of a file in 4k chunks. Useful for low
                    memory machines because it doesnt load the entire file in
                    RAM.

    Args:
        filename (str) - Path to file.

    Returns:
        Hexadecimal string of the hash on success.
        None if the hash couldn't be calculated.
    """
    md5hash = hashlib.md5()

    try:
        with open(filename, "rb") as filep:
            for chunk in iter(lambda: filep.read(4096), b""):
                md5hash.update(chunk)
    except PermissionError:
        return None
    return md5hash.hexdigest()


def count_files(path):
    """count_files() - Count all files in a directory and its included sub
                       directories.

    Args:
        path (str) - Path to file or directory to count files.

    Returns:
        Number of files counted (int)
    """
    if os.path.isfile(path):
        return 1

    count = 0
    for _, _, files in os.walk(path):
        count += len(files)
    return count


def calculate_hashes(path):
    """calculate_hashes() - Calculate MD5 hashes of all files within a
                            directory, adding them to a bloom filter.

    Args:
        path (str) - Path to directory containing files to hash.

    Returns:
        Nothing
    """
    if os.path.isfile(path):
        digest = md5_file(path)
        #digest = md5_first_8192(path)
        if digest:
            print("  ", path, digest)
            bloomfilter.add(digest)
        else:
            return
    for root, _, files in os.walk(path):
        for filename in files:
            fullpath = os.path.join(root, filename)

            # We only care about files.
            if not os.path.isfile(fullpath):
                continue

            #digest = md5_first_8192(fullpath)
            digest = md5_file(fullpath)
            if digest:
                print("  ", fullpath, digest)
                bloomfilter.add(digest)
            else:
                print(fullpath, "Permission Denied")


def lookup_hashes(path):
    """lookup_hashes() - Determine if files within a directory have hashes
                         within a bloom filter.

    Args:
        path (str) - Path to directory to check.

    Returns:
        Nothing.
    """
    if os.path.isfile(path):
        #digest = md5_first_8192(path)
        digest = md5_file(path)
        if digest and bloomfilter.lookup(digest) is False:
            print("%s is not in filter" % path)
        else:
            # TODO: logic to print these
            pass
            #print("%s is in filter" % path)
        return
    for root, _, files in os.walk(path):
        for filename in files:
            fullpath = os.path.join(root, filename)

            # We only care about files.
            if not os.path.isfile(fullpath):
                continue

            #digest = md5_first_8192(fullpath)
            digest = md5_file(fullpath)
            if digest and bloomfilter.lookup(digest) is False:
                print("%s is not in filter" % fullpath)
            else:
                print("%s is in filter" % fullpath)


def usage(progname):
    """usage() - Print CLI usage help message and exit

    Args:
        progname (str) - Name of the program.

    Returns:
        Nothing.
    """
    sys.stderr.write("usage: %s <calculate|lookup> <filterfile> <file1> [file2 ...]\n" % progname)
    exit(os.EX_USAGE)


def readable_file(path):
    if os.path.isfile(path) and os.access(path, os.R_OK):
        return True
    return False


def writeable_file(path):
    try:
        with open(path, "wb"):
            return True
    except PermissionError:
        return False


def main():
    global bloomfilter

    try:
        command = sys.argv[1]
        filterfile = sys.argv[2]
        files = sys.argv[3:]
    except IndexError:
        usage(sys.argv[0])

    if files == [] or sys.argv[1] not in ["calculate", "lookup"]:
        usage(sys.argv[0])

    if command == "lookup":
        if not readable_file(filterfile):
            sys.stdout.write("[-] Unable to open %s for reading\n" % filterfile)
            usage(sys.argv[0])

        bloomfilter = BloomFilter(1, 0.01)
        bloomfilter.load(filterfile)

        for item in files:
            lookup_hashes(item)
        #print("[+] Done.")

    if command == "calculate":
        if not writeable_file(filterfile):
            sys.stdout.write("[-] Unable to open %s for writing\n" % filterfile)
            usage(sys.argv[0])

        print("[+] Counting files. This may take a while")
        size = 0
        for item in files:
            size += count_files(item)
        print("    Counted %d files." % size)

        bloomfilter = BloomFilter(size, 0.01)

        print("[+] Calculating hashes.")
        for item in files:
            calculate_hashes(item)

        print("[+] Saving %s filter to outfile: %s" % \
            (bloomfilter.bytesize_human(), filterfile))
        bloomfilter.save(filterfile)
        print("[+] Done.")


if __name__ == "__main__":
    main()

