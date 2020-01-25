#!/usr/bin/env python3

"""
Calculate hashes from NIST NSRL datasets
"""

import csv
from dmfrbloom import bloomfilter

OS = {}
with open("NSRLOS.txt") as csvfile:
    os_reader = csv.reader(csvfile)
    next(os_reader) # Skip header
    for row in os_reader:
        OS[row[0]] = row[1]

PROD = {}
with open("NSRLProd.txt") as csvfile:
    prod_reader = csv.reader(csvfile)
    next(prod_reader)
    for row in prod_reader:
        PROD[row[0]] = [row[1], OS[row[3]]]

COUNT = {}
for key in PROD:
    COUNT[PROD[key][1]] = 0

with open("NSRLFile.txt", encoding="utf-8", errors="ignore") as csvfile:
    file_reader = csv.reader(csvfile)
    next(file_reader)
    for row in file_reader:
        #try:
        #print(row)
        #print(row[1], PROD[row[5]][1], ascii(row[3]))
        COUNT[PROD[row[5]][1]] += 1
        #except KeyError:
        #    pass
        #except IndexError:
        #    print()
        #    print(row)
        #    print(PROD[row[5]])
        #    exit()

BF = {}
for x in COUNT:
    print(x, COUNT[x])
    if COUNT[x] == 0:
        continue
    BF[x] = bloomfilter.BloomFilter(COUNT[x], 0.01)

count = 0
with open("NSRLFile.txt", encoding="utf-8", errors="ignore") as csvfile:
    file_reader = csv.reader(csvfile)
    next(file_reader)
    for row in file_reader:
        count += 1
        if count % 10000 == 0:
            print(row[1].lower())
        BF[PROD[row[5]][1]].add(row[1].lower())

for x in BF:
    print(x)
    BF[x].save("filters/" + x.replace("/", "").replace(" ", "_"))
