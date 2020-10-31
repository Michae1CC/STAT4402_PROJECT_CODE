#!/usr/bin/env python3

__author__ = 'Michael Ciccotosto-Camp'
__version__ = ''

import itertools
import os
import sys

from glob import glob

from pprint import pprint

if sys.platform.startswith('win32'):
    PROJECT_DIR = os.path.join(
        'D:\\', '2020', 'S2', 'STAT_4402', 'ASSESSMENT', 'STAT4402_PROJECT_CODE')
elif sys.platform.startswith('linux'):
    PROJECT_DIR = os.path.join(
        '/', 'home', 's4430291', 'Courses', 'STAT4402', 'STAT4402_PROJECT_CODE')


def get_test_perfection(filepath):

    with open(filepath) as filepointer:
        content = filepointer.readlines()

    content_iter = (line.strip() for line in content)
    content_iter = itertools.dropwhile(lambda line: not line.lower().startswith(
        "TEST data meterics:".lower()), content_iter)
    content_iter = itertools.dropwhile(lambda line: not line.lower().startswith(
        "Molecular Perfection rate:".lower()), content_iter)

    # Grab the str with the molecular perfection rate

    perf_str = next(content_iter)

    _, perf_str, *_ = perf_str.split("  ")

    perf_float = float(perf_str)

    return perf_float


# Get all the files paths from the auto param out directory
auto_param_out_path = os.path.join(
    PROJECT_DIR, 'data', 'auto_out2', 'batch_out')

all_files = glob(os.path.join(auto_param_out_path, "*.txt"))

perfection_tups = []

for filename in all_files:

    perf_float = None

    try:
        perf_float = get_test_perfection(filename)
    except StopIteration:
        continue

    perfection_tups.append((perf_float, os.path.basename(filename)))


# Create a list of tuples with perfection rate and basename
# perfection_tups = list((get_test_perfection(filename),
#                         os.path.basename(filename)) for filename in all_files)
perfection_tups = sorted(perfection_tups, key=lambda tup: tup[0])
pprint(perfection_tups[-5:])
