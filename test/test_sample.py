#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test sampling instances
"""

# TODO:
# -write proper tests which do not rely on visual inspection


import unittest
import StringIO

from tt.sample import *

from common import DATA_DIR


class Test_sample(unittest.TestCase):
    
    def setUp(self):
        self.inf = open(DATA_DIR + "/dimin.train")
    
    def test_class_count(self):
        class_count = get_class_counts(self.inf, sep=",")
        print_class_dist(class_count)
        
        
    def test_downsampling(self):
        outf = StringIO.StringIO()
        sample_down(self.inf, {"T": 0.5, "K": 0.5}, sep=",", outf=outf)
        outf = outf.getvalue().split("\n")
        class_count = get_class_counts(outf, sep=",")
        print_class_dist(class_count)
        
        
        
        

if __name__ == '__main__':
    unittest.main()    