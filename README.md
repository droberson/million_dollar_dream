# MILLION DOLLAR DREAM
Every man has a price.

This creates a bloom filter to store and lookup file hashes in a space efficent
manner. 

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


