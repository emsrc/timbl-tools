#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generate graph of feature weights

Reads feature weight from Timbl trace file and writes ascii graphs of the
relative feature weights, for each of the different feature weighting schemes,
to standard output.

Example:
  $ Timbl -f dimin.train |tt-feat-weight-graph.py
"""

import sys

from tt.argparse import ArgumentParser, RawDescriptionHelpFormatter
from tt.featgraph import ( parse_feat_weights, 
                           parse_feature_names, 
                           graph_table, 
                           print_table )

__author__ = 'Erwin Marsi <e.marsi@gmail.com>'
__version__ = "0.5"

        
parser = ArgumentParser(description=__doc__,
                        version="%(prog)s version " + __version__,
                        formatter_class=RawDescriptionHelpFormatter)

parser.add_argument("-n", "--names",
                    metavar="FILE",
                    help="file with feature names, one per line")

parser.add_argument("-t", "--table",
                    action='store_true',
                    help="also print feature weight table")

args = parser.parse_args()



if args.names: 
    feat_names = parse_feature_names(args.names)
else:
    feat_names = []
    

field_names, table = parse_feat_weights(sys.stdin, feat_names)    
    
graph_table(field_names, table)

if args.table:
    print_table(field_names, table)
    
