#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# \file test_SSLTrasport.py
# \brief
# \date $Date: $
# \author Nobuhiko Miyamoto
#


import threading
import os
import multiprocessing
import RTC
import OpenRTM_aist
import time
import sys
sys.path.insert(1, "../")

try:
    import unittest2 as unittest
except (ImportError):
    import unittest


#from Manager import *


def RunOutPort(q):

    argv = sys.argv[:]
    #argv.extend(['-o', 'corba.endpoint::2810'])

    manager = OpenRTM_aist.Manager.init(argv)
    manager.activateManager()
    _d_out = RTC.TimedLong(RTC.Time(0, 0), 0)
    _outOut = OpenRTM_aist.OutPort("out", _d_out)
    prop = OpenRTM_aist.Properties()
    _outOut.init(prop)

    """orb = manager.getORB()
    poa = orb.resolve_initial_references("omniINSPOA")
    poa._get_the_POAManager().activate()
    id = "test"
    poa.activate_object_with_id(id, _outOut)"""

    manager._namingManager.bindPortObject("test", _outOut)

    q.get()

    _d_out.data = 100
    _outOut.write()

    q.get()

    manager.shutdown()


class TestSSLTransport(unittest.TestCase):

    def setUp(self):
        self.queue = multiprocessing.Queue()

        sys.argv.extend(['-o', 'manager.preload.modules:SSLTransport.py'])
        sys.argv.extend(['-o', 'manager.modules.load_path:./,../'])
        sys.argv.extend(
            ['-o', 'corba.ssl.certificate_authority_file:root.crt'])
        sys.argv.extend(['-o', 'corba.ssl.key_file:server.pem'])
        sys.argv.extend(['-o', 'corba.ssl.key_file_password:password'])
        os.environ['ORBsslVerifyMode'] = "none"
        self.outport_process = multiprocessing.Process(
            target=RunOutPort, args=(self.queue,))
        self.outport_process.start()

        time.sleep(1)
        os.environ['ORBtraceLevel'] = '25'

        self.manager = OpenRTM_aist.Manager.init(sys.argv)
        self.manager.activateManager()
        self._d_in = RTC.TimedLong(RTC.Time(0, 0), 0)
        self._inIn = OpenRTM_aist.InPort("in", self._d_in)
        prop = OpenRTM_aist.Properties()
        self._inIn.init(prop)
        self.inport_obj = self._inIn.getPortRef()

        orb = self.manager.getORB()
        #outport_name = "corbaloc:iiop:localhost:2810/test"
        outport_name = "corbaname::localhost:2809/NameService#test"
        oobj = orb.string_to_object(outport_name)
        self.outport_obj = oobj._narrow(RTC.PortService)

    def tearDown(self):
        self.manager.shutdownManager()
        self.queue.put("")

    def test_Connect(self):

        prop = OpenRTM_aist.Properties()
        ret = OpenRTM_aist.connect(
            "con1", prop, self.inport_obj, self.outport_obj)

        self.queue.put("")

        #ret = self._inIn.isNew()
        #data = self._inIn.read()

        # self.outport_obj.disconnect_all()


############### test #################
if __name__ == '__main__':
    unittest.main()
