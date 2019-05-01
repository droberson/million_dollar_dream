#!/usr/bin/env python3

"""
This tool will create and compare bloom filters containing file hashes. It
will be useful to see which files are new or have changed on a host, provided
a filter has been pre-calculated.

Example:
    ./million_dollar_dream.py calculate ubuntu-16.04.filter /bin /sbin /etc /usr
    ./million_dollar_dream.py lookup ubuntu-16.04.filter /bin/bash
    ...
    This will show what is/isn't in the filter
    ...

TODO:
    - Test on big endian machine
    - Make as many filters as possible for likely software
        - Ubuntu distros
        - Debian distros
        - CentOS distros
    - Test on Windows?
    - Test on python2.7
        - to_bytes and from_bytes do not work.
"""

from million_dollar_dream.main import main


if __name__ == "__main__":
    main()
