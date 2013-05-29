#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Down-sampling Timbl instances

Reads Timbl instances from standard input and writes down-sampled instances to
standard output. Amount of down-sampling can be specified per class.

Example:
$ tt-down-sample.py T:0.1 -d, < ../data/dimin.train 
"""

import sys

from tt.argparse import ArgumentParser, RawDescriptionHelpFormatter
from tt.sample import sample_down

__author__ = 'Erwin Marsi <e.marsi@gmail.com>'
__version__ = "0.5"

        
parser = ArgumentParser(description=__doc__,
                        version="%(prog)s version " + __version__,
                        formatter_class=RawDescriptionHelpFormatter)

parser.add_argument("class_fracts",
                    metavar="CLASS:FRACTION",
                    nargs="+",
                    help="targeted size reduction per class ")

parser.add_argument("-d", "--delimiter",
                    default=None,
                    metavar="CHAR",
                    help="field delimiter in instances "
                    "(default is whitespace)")

args = parser.parse_args()

class_fracts = {}

for spec in args.class_fracts:
    class_, fract = spec.split(":")
    fract = float(fract)
    assert 0 <= fract <= 1.0
    class_fracts[class_] = fract

sample_down(sys.stdin, class_fracts, sep=args.delimiter)
