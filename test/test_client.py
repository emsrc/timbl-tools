#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test TimblClient class
"""

import logging
import unittest

from tt.server import TimblServer
from tt.client import TimblClient, TimblClientError

from common import DATA_DIR

SERVER = None


def start_timbl_server():
    global SERVER
    
    options = "-f {0}/dimin.train".format(DATA_DIR)
    SERVER = TimblServer(timbl_opts=options)
    SERVER.start()


class Test_TimblClient(unittest.TestCase):
    
    def setUp(self):
        if not SERVER:
            start_timbl_server()
            
        self.client = TimblClient(SERVER.port)
        self.client.connect()
        
        
    def test_disconnect(self):
        self.client.disconnect()
        self.assertRaises(TimblClientError, self.client.query)
        self.assertFalse(self.client.socket)

        
    def test_reconnect(self):
        self.client.reconnect()
        self.client.query()
        
        
    def test_connection_timeout(self):
        # send incomplete command so server does not reply
        self.client.socket.settimeout(1)
        self.assertRaises(TimblClientError, 
                          self.client.set, 
                          "-k")
        self.client.socket.settimeout(10)
        

    def test_query(self):
        # repeat multiple times, because recv in multiple parts occurs rarely
        for i in range(25):
            status = self.client.query()
            ## print status
            self.assertEqual(status["NEIGHBORS"], "1")
            
            
    def test_set(self):
        self.client.set("-k 10 -d IL")
        status = self.client.query()
        self.assertEqual(status["NEIGHBORS"], "10")
        self.assertEqual(status["DECAY"], "IL")
        self.client.set("-k 1 -d Z")        
    
    def test_set_error(self):
        self.assertRaises(TimblClientError, 
                          self.client.set, 
                          "-w 1")
        
        
    def test_classify(self):
        """
        Exhaustively test classification with any combination of the verbose
        output options +/-vdb (distribution), +/-vdi (distance) and +/-vn
        (neighbours). The +/-vk seems to be unsupported, as it cannot be "set"
        through the server
        """
        self.client.set("-k10") 

        for db in "+vdb -vdb".split(): 
            for di in "+vdi -vdi".split():
                for vn in "+vn -vn".split():
                    self.client.set(db + " " + di + " " + vn)

                    for i, inst in enumerate(open(DATA_DIR + "/dimin.train")):
                        if i > 10: break
                        result = self.client.classify(inst)
                        
                        self.assertTrue(result.has_key("CATEGORY"))
                        
                        if db == "+vdb":
                            self.assertTrue(result.has_key("DISTRIBUTION"))
                        else:
                            self.assertFalse(result.has_key("DISTRIBUTION"))
                            
                        if di == "+vdi":
                            self.assertTrue(result.has_key("DISTANCE"))
                        else:
                            self.assertFalse(result.has_key("DISTANCE"))
                            
                        if vn == "+vn":
                            self.assertTrue(result.has_key("NEIGHBOURS"))
                        else:
                            self.assertFalse(result.has_key("NEIGHBOURS"))
                        
        self.client.set("-k1 -vdb -vdi -vn") 
                        

        
    def test_classify_error(self):
        self.assertRaises(TimblClientError, 
                          self.client.classify,
                          "x, x, x, x")
        
    def test_log(self):
        # quick & global config of logging system so output of loggers
        # goes to stdout
        logging.basicConfig(level=logging.DEBUG,
                            format="%(levelname)-8s <%(name)s> :: %(message)s")
        
        self.client = TimblClient(SERVER.port, log_tag="test_log_client")
        self.client.connect()
        
        instances = open(DATA_DIR + "/dimin.train").readlines()
        
        for inst in instances[:2]:
            self.client.classify(inst)
            
        self.client.query()
        
        self.client.set("+vdb +vdi +vn")
        
        for inst in instances[:2]:
            self.client.classify(inst)
            
        try:
            self.client.classify("x, x")
        except TimblClientError:
            pass
                    
        try:
            self.client.set("-w 1")
        except TimblClientError:
            pass
        
        self.client.disconnect()
        
        # global reset of logging level
        logging.getLogger().setLevel(logging.CRITICAL)

        
        
    def tearDown(self):
        self.client.disconnect()
        


if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()            
        