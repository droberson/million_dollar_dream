#!/usr/bin/env python3

"""
  compile python scripts as ELF.
  based on https://gist.github.com/itdaniher/46fec3dd3b7eb603d7cbb5cd55fa5e1d


  pip3 install Cython

  static linking is possible adding -static flag and -l for each required
  library. modify the globals to do this.

"""

from os import EX_USAGE
from sys import argv
from subprocess import check_call
from tempfile import NamedTemporaryFile
from Cython.Compiler import Main

        #libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f3859f5d000)
        #libpthread.so.0 => /lib/x86_64-linux-gnu/libpthread.so.0 (0x00007f3859d40000)
        #libexpat.so.1 => /lib/x86_64-linux-gnu/libexpat.so.1 (0x00007f3859b17000)
        #libz.so.1 => /lib/x86_64-linux-gnu/libz.so.1 (0x00007f38598fd000)
        #libdl.so.2 => /lib/x86_64-linux-gnu/libdl.so.2 (0x00007f38596f9000)
        #libutil.so.1 => /lib/x86_64-linux-gnu/libutil.so.1 (0x00007f38594f6000)
        #libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x00007f38591ed000)

# You might need to change these.
IFLAGS = "-I/usr/include/python3.5"
LFLAGS = "-L/usr/lib/python3.5"
CFLAGS = "-fPIC -static -static-libgcc"
LIBRARIES = "-lpython3.5m -ldl -lutil -lexpat -lpthread -lz -lm"


def main():
    """
    This will do ugly things to compile a python file.
    """
    try:
        source = open(argv[1]).read()
        outfile = argv[1].replace(".py", ".out")
    except IndexError:
        print("usage: ./compile.py <python file>")
        exit(EX_USAGE)

    temp_py_file = NamedTemporaryFile(suffix=".py", delete=False)
    temp_py_file.write(source.encode())
    temp_py_file.flush()

    Main.Options.embed = "main"
    res = Main.compile_single(temp_py_file.name, Main.CompilationOptions(), "")

    gcc_cmd = "gcc %s %s %s %s %s -o %s" % \
        (CFLAGS, res.c_file, LFLAGS, IFLAGS, LIBRARIES, outfile)

    print(gcc_cmd)
    check_call(gcc_cmd.split(" "))


if __name__ == "__main__":
    main()
