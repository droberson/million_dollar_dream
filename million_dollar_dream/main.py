from datetime import datetime
import hashlib
import json
import os
import sys
import urllib.request

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
    message = (
        "usage: %s <calculate|lookup|fromfile|filters> "
        "<filterfile> <file1> [file2 ...]\n"
    ) % progname
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


def get_config():
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, "config.json")
    try:
        with open(path, "rb") as f:
            config = f.read()
            config = json.loads(config)
    except FileNotFoundError:
        config = dict(
            hash_alg="sha256",
            repo="https://github.com/roberson-io/mdd_filters/raw/master/repo/",
        )
    with open(path, "w") as f:
        f.write(json.dumps(config, sort_keys=True, indent=4))
    return config


def update_metadata(repo_url=None):
    if not repo_url:
        config = get_config()
        repo_url = config["repo"]
    url = repo_url + "METADATA.json"
    with urllib.request.urlopen(url) as f:
        metadata = f.read().decode("utf-8")
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, "METADATA.json")
    with open(path, "w") as f:
        f.write(metadata)
    return json.loads(metadata)


def get_metadata():
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, "METADATA.json")
    try:
        with open(path, "rb") as f:
            metadata = f.read()
            metadata = json.loads(metadata)
    except FileNotFoundError:
        metadata = update_metadata()
    return metadata


def hasher(hash_alg):
    if hash_alg == "md5":
        return hashlib.md5()
    elif hash_alg == "sha1":
        return hashlib.sha1()
    elif hash_alg == "sha256":
        return hashlib.sha256()
    else:
        message = "[-] Invalid hash algorithm: %s" % hash_alg
        sys.stderr.write(message)
        exit(os.EX_USAGE)


def get_installed(hash_alg=None):
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, "installed.json")
    try:
        with open(path, "rb") as f:
            installed = f.read()
            installed = json.loads(installed)
    except FileNotFoundError:
        installed = dict()
        filters = os.path.join(dirname, "filters")
        if not hash_alg:
            config = get_config()
            hash_alg = config["hash_alg"]
        for file_name in os.listdir(filters):
            filter_path = os.path.join(filters, file_name)
            hash_func = hasher(hash_alg)
            with open(filter_path, "rb") as f:
                buffer = f.read()
                hash_func.update(buffer)
                mtime = os.path.getmtime(filter_path)
                last_modified = datetime.fromtimestamp(mtime)
            installed[file_name] = dict(
                description="",
                last_modified=last_modified.isoformat(),
                hash=dict(alg=hash_alg, digest=hash_func.hexdigest()),
            )
        with open(path, "w") as f:
            f.write(json.dumps(installed, sort_keys=True, indent=4))
    return installed


def print_filters(data):
    print(
        "{0: <{width}}".format("Filter", width=20),
        "{0: <{width}}".format("Description", width=40),
        "{0: <{width}}".format("Last modified", width=20),
    )
    print("-" * 90)
    for filter_name in data.keys():
        filter_data = data[filter_name]
        print(
            "{0: <{width}}".format(filter_name, width=20),
            "{0: <{width}}".format(filter_data["description"], width=40),
            "{0: <{width}}".format(filter_data["last_modified"], width=20),
        )


def list_local(hash_alg=None):
    installed = get_installed(hash_alg)
    print_filters(installed)


def list_remote(repo):
    remote = update_metadata(repo)
    print_filters(remote)


def is_installed(target):
    installed = get_installed()
    dirname = os.path.dirname(__file__)
    filters = os.path.join(dirname, "filters")
    return bool(target in installed.keys() and target in os.listdir(filters))


def download_filter(target):
    config = get_config()
    repo = config["repo"]
    url = repo + target
    try:
        print("Fetching %s..." % target)
        with urllib.request.urlopen(url) as f:
            filter_data = f.read()
        dirname = os.path.dirname(__file__)
        filter_path = os.path.join(dirname, "filters")
        path = os.path.join(filter_path, target)
        with open(path, "wb") as f:
            f.write(filter_data)
        print("Done.")
    except urllib.error.HTTPError:
        print("%s filter not found!" %  target)
        exit()



def update_installed(target):
    metadata = update_metadata()
    config = get_config()
    hash_alg = config["hash_alg"]
    installed = get_installed(hash_alg)
    target_data = metadata[target]
    installed[target] = dict(
        description=target_data["description"],
        hash=dict(alg=hash_alg, digest=target_data[hash_alg]),
        last_modified=target_data["last_modified"],
    )
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, "installed.json")
    with open(path, "w") as f:
        f.write(json.dumps(installed, sort_keys=True, indent=4))


def fetch_filter(target):
    if is_installed(target):
        print("%s is already installed" % target)
    else:
        download_filter(target)
        update_installed(target)


def update_filters():
    config = get_config()
    hash_alg = config["hash_alg"]
    installed = get_installed(hash_alg)
    metadata = update_metadata()
    for target in installed.keys():
        if target in metadata.keys():
            here_data = installed[target]
            there_data = metadata[target]
            modified_here = datetime.strptime(
                here_data["last_modified"], "%Y-%m-%dT%H:%M:%S.%f"
            )
            modified_there = datetime.strptime(
                there_data["last_modified"], "%Y-%m-%dT%H:%M:%S.%f"
            )
            hash_here = here_data["hash"]["digest"]
            hash_there = there_data[hash_alg]
            if (modified_there > modified_here) and (hash_there != hash_here):
                print("Updating %s..." % target)
                download_filter(target)
                update_installed(target)
                print("Done.")


def main():

    try:
        command = sys.argv[1]
        if command == "filters":
            filter_command = sys.argv[2]
            if len(sys.argv) > 3:
                target = sys.argv[3]
            else:
                target = None
        else:
            filterfile = sys.argv[2]
            files = sys.argv[3:]
    except IndexError:
        usage(sys.argv[0])

    if sys.argv[1] not in ["calculate", "lookup", "fromfile", "filters"]:
        usage(sys.argv[0])
    if sys.argv[1] != "filters" and not files:
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

        print(
            "[+] Saving %s filter to outfile: %s"
            % (bloomfilter.bytesize_human, filterfile)
        )
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
        print(
            "[+] Saving %s filter to outfile: %s"
            % (bloomfilter.bytesize_human, filterfile)
        )
        bloomfilter.save(filterfile)
        print("[+] Done.")

    if command == "filters":
        config = get_config()
        if filter_command not in ["fetch", "list", "update"]:
            usage(sys.argv[0])
        if filter_command == "fetch":
            if not target:
                usage(sys.argv[0])
            else:
                fetch_filter(target)
        if filter_command == "list":
            if not target:
                list_local(config["hash_alg"])
            elif target == "remote":
                list_remote(config["repo"])
            else:
                list_remote(target)
        if filter_command == "update":
            update_filters()
