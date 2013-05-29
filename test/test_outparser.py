#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test Timbl output parsing
"""

import unittest

from tt.outparser import *

from common import DATA_DIR


class Test_outparser(unittest.TestCase):
    
    def setUp(self):
        pass
    
    
    def test_parse_timbl_output_1(self):
        timbl_output = open(DATA_DIR + "/sample.out")
        
        parser = parse_timbl_output(timbl_output)
        
        inst_str, k_nn_list = parser.next()
        self.assertEqual(len(k_nn_list), 20)
        
        inst_str, k_nn_list = parser.next()
        self.assertEqual(len(k_nn_list), 8)
        
        inst_str, k_nn_list = parser.next()
        self.assertEqual(len(k_nn_list), 11)
                
        self.assertRaises(StopIteration, parser.next)
        
    
    def test_parse_timbl_output_2(self):
        timbl_output = open(DATA_DIR + "/sample.out")
        for inst_str, k_nn_list in parse_timbl_output(timbl_output):
            pass
        
    
    def test_parse_inst_space(self):
        inst = "= = = = = = = = + p e = T P\n"
        feats_str, true_class, pred_class = parse_inst(inst)[:3]

        self.assertEqual(feats_str, "= = = = = = = = + p e =")
        self.assertEqual(true_class, "T")
        self.assertEqual(pred_class, "P")
        
    def test_parse_inst_comma(self):
        inst = "=,=,=,=,=,=,=,=,+,p,e,=,T,P\n"
        feats_str, true_class, pred_class = parse_inst(inst, feat_sep=",")[:3]

        self.assertEqual(feats_str, "=,=,=,=,=,=,=,=,+,p,e,=")
        self.assertEqual(true_class, "T")
        self.assertEqual(pred_class, "P")

        
    def test_parse_inst_with_distrib_space(self):
        inst = "= = = = + k u = - bl u m E P { E 6.00000, P 16.0000 }\n"
        feats_str, true_class, pred_class, distrib_str = \
        parse_inst(inst, with_distrib=True)[:4]

        self.assertEqual(feats_str, "= = = = + k u = - bl u m")
        self.assertEqual(true_class, "E")
        self.assertEqual(pred_class, "P")
        self.assertEqual(distrib_str, "E 6.00000, P 16.0000")
        
    def test_parse_inst_with_distrib_comma(self):
        inst = "=,=,=,=,+,k,u,=,-,bl,u,m,E,P { E 6.00000, P 16.0000 }\n"
        feats_str, true_class, pred_class, distrib_str = \
        parse_inst(inst, with_distrib=True, feat_sep=",")[:4]

        self.assertEqual(feats_str, "=,=,=,=,+,k,u,=,-,bl,u,m")
        self.assertEqual(true_class, "E")
        self.assertEqual(pred_class, "P")
        self.assertEqual(distrib_str, "E 6.00000, P 16.0000")
        
        
    def test_parse_inst_with_dist_space(self):
        inst = "= = = = = = = = + sx E lm P J        0.042844587034556\n"
        feats_str, true_class, pred_class, distrib_str, dist = \
        parse_inst(inst, with_distance=True)

        self.assertEqual(feats_str, "= = = = = = = = + sx E lm")
        self.assertEqual(true_class, "P")
        self.assertEqual(pred_class, "J")
        self.assertAlmostEqual(dist, 0.042844587034556)
        
    def test_parse_inst_with_dist_comma(self):
        inst = "=,=,=,=,=,=,=,=,+,sx,E,lm,P,J        0.042844587034556\n"
        feats_str, true_class, pred_class, distrib_str, dist = \
        parse_inst(inst, with_distance=True, feat_sep=",")

        self.assertEqual(feats_str, "=,=,=,=,=,=,=,=,+,sx,E,lm")
        self.assertEqual(true_class, "P")
        self.assertEqual(pred_class, "J")
        self.assertAlmostEqual(dist, 0.042844587034556)
        
        
    def test_parse_inst_with_distrib_with_dist_space(self):
        inst = "= = = = = = = = + sx E lm P J { T 12.0000, E 41.0000, J 56.0000, P 14.0000 }        0.042844587034556\n"
        feats_str, true_class, pred_class, distrib_str, dist = \
        parse_inst(inst, with_distrib=True, with_distance=True)

        self.assertEqual(feats_str, "= = = = = = = = + sx E lm")
        self.assertEqual(true_class, "P")
        self.assertEqual(pred_class, "J")
        self.assertEqual(distrib_str, "T 12.0000, E 41.0000, J 56.0000, P 14.0000")
        self.assertAlmostEqual(dist, 0.042844587034556)
        
    def test_parse_inst_with_distrib_with_dist_comma(self):
        inst = "=,=,=,=,=,=,=,=,+,sx,E,lm,P,J { T 12.0000, E 41.0000, J 56.0000, P 14.0000 }        0.042844587034556\n"
        feats_str, true_class, pred_class, distrib_str, dist = \
        parse_inst(inst, with_distrib=True, with_distance=True, feat_sep=",")

        self.assertEqual(feats_str, "=,=,=,=,=,=,=,=,+,sx,E,lm")
        self.assertEqual(true_class, "P")
        self.assertEqual(pred_class, "J")
        self.assertEqual(distrib_str, "T 12.0000, E 41.0000, J 56.0000, P 14.0000")
        self.assertAlmostEqual(dist, 0.042844587034556)
        
    
    def test_parse_distrib(self):
        distrib_str = " T 2.00000, E 61.0000, J 76.0000, P 7.00000, K 28.0000 "
        
        for class_, count in parse_distrib(distrib_str):
            self.assertTrue(class_ in "TEJPK")
            self.assertTrue(isinstance(count, float))
            
            
    def test_parse_neighbour_vk_vdi(self):
        nn_str = "# k=4\t{ T 1.00000, J 79.0000 }\t0.22791476779488\n"
        distrib_str, distance = parse_neighbour_vk_vdi(nn_str)
        
        self.assertEqual(distrib_str, "T 1.00000, J 79.0000")
        self.assertAlmostEqual(distance, 0.22791476779488)
        
        
    def test_parse_distance_vn_vdb(self):
        nn_str = "# k=2, 14 Neighbor(s) at distance:\t0.042844587034556\n"
        distance = parse_distance_vn_vdb(nn_str)

        self.assertAlmostEqual(distance, 0.042844587034556)
        
        
    def test_parse_neighbour_vn_vdb_space(self):
        nn_str = "#\t= = = = = = = = + p e = { T 1.00000 }\n"
        feats, class_ = parse_neighbour_vn_vdb(nn_str)
        
        self.assertEqual(feats, "= = = = = = = = + p e =")
        self.assertEqual(class_, "T")
        
    def test_parse_neighbour_vn_vdb_comma(self):
        nn_str = "#\t=,=,=,=,=,=,=,=,+,p,e,=,{ T 1.00000 }\n"
        feats, class_ = parse_neighbour_vn_vdb(nn_str, feat_sep=",")
        
        self.assertEqual(feats, "=,=,=,=,=,=,=,=,+,p,e,=")
        self.assertEqual(class_, "T")
        
        
    def tearDown(self):
        pass
        
        
        

if __name__ == '__main__':
    unittest.main()    