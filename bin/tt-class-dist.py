#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Show class distribution of Timbl instances

Reads Timbl instances from standard input and writes a class distribution in
the form of an ascii table to standard output.

Example:
  $ tt-class-dist.py -d, < ../data/dimin.train 
"""

import sys

from tt.argparse import ArgumentParser, RawDescriptionHelpFormatter
from tt.sample import get_class_counts, print_class_dist

__author__ = 'Erwin Marsi <e.marsi@gmail.com>'
__version__ = "0.5"

        
parser = ArgumentParser(description=__doc__,
                        version="%(prog)s version " + __version__,
                        formatter_class=RawDescriptionHelpFormatter)

parser.add_argument("-d", "--delimiter",
                    default=None,
                    metavar="CHAR",
                    help="field delimiter in instances "
                    "(default is whitespace)")

args = parser.parse_args()

class_counts = get_class_counts(sys.stdin, sep=args.delimiter)
print_class_dist(class_counts)
