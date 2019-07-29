# MILLION DOLLAR DREAM
Every man has a price.

This project assumes you have a whole boat load (10k+?) of files you have calculated
a baseline of and that you want to compare to see if any have changed.  This 
creates a bloom filter to store and lookup file hashes in a space efficient
manner. 

## OPTIONS

```bash
python3 ./million_dollar_dream.py 
usage: ./million_dollar_dream.py <calculate|lookup|fromfile|filters> <filterfile> <file1> [file2 ...]
```

* calculate - given an input of file(s), calculate all the hashes and store them in the filter file
* lookup - tbd
* fromfile - tbd
* filters - given an input of file(s), see if any of them have changed based on the  the filter 
file. Returns `is not in filter` and `is in filter` for every file input

## USAGE

### Calculate 
The first step is to create your bloom filters as a baseline of what
you'll use in the future.  You may choose to have multiple filter files
you'll use or one master one.  Assuming you have your source files in
`./source_dir` which you want to make hashes of to store in your filter. 
This dir has 3 files:

```bash
./source_dir
./source_dir/a_file.txt
./source_dir/b_file.txt
./source_dir/c_file.txt
```

Also, let's assume you want store you filter in `/tmp/bloom`. So if
you're in this `million_dollar_dream` repo you just checked out, you'd run:

```bash
python3 ./million_dollar_dream.py calculate /tmp/bloom ./source_dir
```

The output would look like this:

```bash
python3 ./million_dollar_dream.py calculate /tmp/bloom ./source_dir
[+] Counting files. This may take a while
    Counted 3 files.
[+] Calculating hashes.
   ./source_dir/b_file.txt c157a79031e1c40f85931829bc5fc552
   ./source_dir/c_file.txt 6e8fe0f63ffbb20d6d202d5520f5051c
   ./source_dir/a_file.txt d3b07384d113edec49eaa6238ad5ff00
[+] Saving 4.0bytes filter to outfile: /tmp/bloom
[+] Done.
```

### Change 

The point of this project is to find files that have changed. So let's
make that happen by edited a file like so:

```bash
echo "foo" >> ./source_dir/b_file.txt
```

### Lookup 

Assuming you don't know which file was edited above, you can run a `filter` call 
based on your previous `calulate` calls. You'll need to grep for `is not in filter` 
to see which file(s) had changed. In our example here, it will show just one:

```bash
python3 ./million_dollar_dream.py lookup /tmp/bloom ./source_dir|grep 'is not in filter'
./source_dir/b_file.txt is not in filter
```


## NOTES
mmh3 library is much more efficient than the pymmh3 included.

## CREDITS
Fredrik Kihlander and Swapnil Gusani for pymmh3.

## TESTING
Create a virtualenv:
```
python3 -m venv /path/to/new/virtual/environment
```

Activate virtualenv:
```
. /path/to/new/virtual/environment/bin/activate
```

Install requirements:
```
pip3 install -r requirements/development.txt
```

Run tests:
```
pytest
```

Run tests with coverage report:
```
pytest --cov-config .coveragerc --cov=million_dollar_dream tests/ --cov-report term-missing
```


