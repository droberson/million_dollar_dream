import os
import sys
import hashlib

from million_dollar_dream.bloomfilter import BloomFilter


def is_md5(string):
    if len(string) != 32:
        return False
    try:
        int(string, 16)
        return True
    except ValueError:
        return False


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


def calculate_hashes(path, bloomfilter):
    """calculate_hashes() - Calculate MD5 hashes of all files within a
                            directory, adding them to a bloom filter.

    Args:
        path (str) - Path to directory containing files to hash.

    Returns:
        Nothing
    """
    if os.path.isfile(path):
        digest = md5_file(path)
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

            digest = md5_file(fullpath)
            if digest:
                print("  ", fullpath, digest)
                bloomfilter.add(digest)
            else:
                print(fullpath, "Permission Denied")


def lookup_hashes(path, bloomfilter):
    """lookup_hashes() - Determine if files within a directory have hashes
                         within a bloom filter.

    Args:
        path (str) - Path to directory to check.

    Returns:
        Nothing.
    """
    if os.path.isfile(path):
        digest = md5_file(path)
        if digest and bloomfilter.lookup(digest) is False:
            print("%s is not in filter" % path)
        else:
            # TODO: logic to print these
            pass
        return
    for root, _, files in os.walk(path):
        for filename in files:
            fullpath = os.path.join(root, filename)

            # We only care about files.
            if not os.path.isfile(fullpath):
                continue

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
    message = ("usage: %s <calculate|lookup|fromfile> "
               "<filterfile> <file1> [file2 ...]\n") % progname
    sys.stderr.write(message)
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

    try:
        command = sys.argv[1]
        filterfile = sys.argv[2]
        files = sys.argv[3:]
    except IndexError:
        usage(sys.argv[0])

    if files == [] or sys.argv[1] not in ["calculate", "lookup", "fromfile"]:
        usage(sys.argv[0])

    if command == "lookup":
        if not readable_file(filterfile):
            message = "[-] Unable to open %s for reading\n" % filterfile
            sys.stdout.write(message)
            usage(sys.argv[0])

        bloomfilter = BloomFilter(1, 0.01)
        bloomfilter.load(filterfile)

        for item in files:
            lookup_hashes(item, bloomfilter)

    if command == "calculate":
        if not writeable_file(filterfile):
            message = "[-] Unable to open %s for writing\n" % filterfile
            sys.stdout.write(message)
            usage(sys.argv[0])

        print("[+] Counting files. This may take a while")
        size = 0
        for item in files:
            size += count_files(item)
        print("    Counted %d files." % size)

        bloomfilter = BloomFilter(size, 0.01)

        print("[+] Calculating hashes.")
        for item in files:
            calculate_hashes(item, bloomfilter)

        print("[+] Saving %s filter to outfile: %s" %
              (bloomfilter.bytesize_human, filterfile))
        bloomfilter.save(filterfile)
        print("[+] Done.")

    if command == "fromfile":
        if not writeable_file(filterfile):
            message = "[-] Unable to open %s for writing\n" % filterfile
            sys.stdout.write(message)
            usage(sys.argv[0])

        print("[+] Counting hashes in %s" % files)
        count = 0
        for hashfile in files:
            print(hashfile)
            with open(hashfile, "r") as hashlist:
                for line in hashlist:
                    # skip comments and lines containing invalid hashes
                    if line.startswith("#") or not is_md5(line.rstrip()):
                        # print("invalid hash: ", line.rstrip())
                        continue
                    count += 1

        print("    Counted %d files." % count)

        bloomfilter = BloomFilter(count, 0.01)

        print("[+] Adding hashes from %s" % files)
        # TODO make sure i can open these files
        for hashfile in files:
            with open(hashfile, "r") as hashlist:
                for line in hashlist:
                    # skip comments and invalid hashes
                    if line.startswith("#") or not is_md5(line.rstrip()):
                        continue
                    bloomfilter.add(line.rstrip().lower())
        print("[+] Saving %s filter to outfile: %s" %
              (bloomfilter.bytesize_human, filterfile))
        bloomfilter.save(filterfile)
        print("[+] Done.")
