#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test TimblServer class
"""

import unittest
import logging
import os
import tempfile

from tt.server import TimblServer, TimblServerError
from tt.log import file_logger

from common import DATA_DIR



class Test_TimblServer(unittest.TestCase):

    def setUp(self):
        self.timbl_opts = "-f {0}/dimin.train".format(DATA_DIR)

    def test_init(self):
        server = TimblServer(timbl_opts=self.timbl_opts)

    def test_start_and_stop(self):
        server = TimblServer(timbl_opts=self.timbl_opts,
                             wait_for_dead=True)
        server.start()
        self.assertTrue(server.pid)
        self.assertTrue(server.pid in server.kill_pids)
        self.assertTrue(os.getpgid(server.pid))

        server_pid = server.pid
        server.stop()
        self.assertFalse(server.pid)
        self.assertFalse(server.pid in server.kill_pids)
        # this requires wait_for_dead=True
        self.assertRaises(OSError, os.getpgid, server_pid)

    def test_start_without_stop(self):
        server = TimblServer(timbl_opts=self.timbl_opts,
                             wait_for_dead=True)
        server.start()
        self.assertTrue(server.pid)
        self.assertTrue(server.pid in server.kill_pids)
        self.assertTrue(os.getpgid(server.pid))

        # server ought to be killed at exit,
        # but there is no way to test that (?)

    def test_restart(self):
        server = TimblServer(timbl_opts=self.timbl_opts,
                             wait_for_dead=True)
        server.start()
        server.restart()
        self.assertTrue(server.pid)
        self.assertTrue(server.pid in server.kill_pids)
        self.assertTrue(os.getpgid(server.pid))

    def test_server_logfile(self):
        log_file = tempfile.NamedTemporaryFile(mode="rb", bufsize=0)
        log_fname= log_file.name
        server = TimblServer(timbl_opts=self.timbl_opts,
                             server_log_fname=log_fname)
        server.start()
        server.stop()
        self.assertTrue(open(log_fname).readlines())

    def test_logging_1(self):
        # quick & global config of logging system so output of loggers
        # goes to stdout
        logging.basicConfig(level=logging.DEBUG,
                            format="%(levelname)s <%(name)s> :: %(message)s")
        server = TimblServer(timbl_opts=self.timbl_opts,
                             wait_for_dead=True,
                             log_tag="server1")
        server.start()
        server.stop()
        # global reset of logging level
        logging.getLogger().setLevel(logging.CRITICAL)
        
    def test_logging_2(self):
        log_fname = tempfile.NamedTemporaryFile().name
        logger = file_logger("my_log", log_fname) 
        server = TimblServer(timbl_opts=self.timbl_opts,
                             logger=logger)
        server.start()
        server.stop()
        #self.assertTrue(open(log_fname).read())
        print open(log_fname).read()
        os.remove(log_fname)

    def test_multiple_servers(self):
        # make sure there are no left overs
        TimblServer.kill_pids = []
        
        for i in range(10):
            server = TimblServer(timbl_opts=self.timbl_opts,
                                 wait_for_dead=True)
            server.start()

        self.assertEqual(len(TimblServer.kill_pids), 10)

        for pid in TimblServer.kill_pids:
            self.assertTrue(os.getpgid(server.pid))



if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()    