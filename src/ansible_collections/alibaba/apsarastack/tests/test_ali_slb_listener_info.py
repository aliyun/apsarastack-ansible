# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import unittest
import uuid


from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vpc import main as vpc_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vswitch import main as vswtich_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_slb_lb_info import main as slb_info_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_slb_lb import main as slb_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_slb_listener import main as slb_listener_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_slb_listener_info import main as slb_listener_info_main

class Test(unittest.TestCase):

    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self.name = "ansible_test_slb_info_%s" % uuid.uuid1()
        self._vpc_info = {
            "cidr_block": "172.16.0.0/16",
            "vpc_name": self.name,
            "description": "create by ansible unit test",
        }
        self._vswtich_info = {
            "cidr_block": "172.16.1.0/24",
            "name": self.name,
        }
        self._slb_args = {
            "internet_charge_type": "PayByTraffic",
            "load_balancer_name": self.name,
            "load_balancer_spec": "slb.s1.small",
            "purge_tags": False
        }

    def setUp(self)->None:
        unittest.TestCase.setUp(self)
        load_dotenv()
        vpc_args = self._vpc_info
        result = run_module(vpc_main, vpc_args)
        self._vpc_info['id'] = result['vpc']['vpc_id']
        self._vswtich_info["vpc_id"] = self._vpc_info['id']
        result = run_module(vswtich_main, self._vswtich_info)
        self._vswtich_info["id"] = result['vswitch']['id']
        self._slb_args["vswitch_id"] = self._vswtich_info["id"]
        result = run_module(slb_main, self._slb_args)
        self._slb_args["id"] = result["load_balancer"]["load_balancer_id"]
        slb_listener_args = {
            "state": "present",
            "listener_port": 80,
            "backend_server_port": 80,
            "load_balancer_id": self._slb_args["id"],
            "bandwidth": 10,
            "sticky_session": "off",
            "protocol": "http"
        }
        run_module(slb_listener_main, slb_listener_args)

        slb_listener_args = {
            "state": "present",
            "listener_port": 70,
            "backend_server_port": 70,
            "load_balancer_id": self._slb_args["id"],
            "bandwidth": 20,
            "protocol": "tcp",
            "health_check": "on"
        }
        run_module(slb_listener_main, slb_listener_args)

        slb_listener_args = {
            "state": "present",
            "listener_port": 60,
            "backend_server_port": 60,
            "load_balancer_id": self._slb_args["id"],
            "bandwidth": 30,
            "protocol": "udp",
            "health_check": "on"
        }
        run_module(slb_listener_main, slb_listener_args)

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        slb_args = {
            "state": "absent",
        } | self._slb_args
        run_module(slb_main, slb_args)
        vswtich_args = {
            "state": "absent",
        } | self._vswtich_info
        run_module(vswtich_main, vswtich_args)
        vpc_args = {
            "state": "absent",
        } | self._vpc_info
        run_module(vpc_main, vpc_args)

    def testDescribeSlbListenerInfo(self):
        slb_args = {
            "load_balancer_id": self._slb_args["id"],
            "listener_port": 80,
            "listener_type": "http",
        }
        result = run_module(slb_listener_info_main, slb_args)
        self.assertNotIn('failed', result)

        slb_args = {
            "load_balancer_id": self._slb_args["id"],
            "listener_port": 70,
            "listener_type": "http",
        }
        result = run_module(slb_listener_info_main, slb_args)
        self.assertIn('failed', result)
        
        slb_args = {
            "load_balancer_id": self._slb_args["id"],
            "listener_type": "tcp",
            "listener_port": 80,
        }
        result = run_module(slb_listener_info_main, slb_args)
        self.assertIn('failed', result)

        slb_args = {
            "load_balancer_id": self._slb_args["id"],
            "listener_type": "tcp",
            "listener_port": 70,
        }
        result = run_module(slb_listener_info_main, slb_args)
        self.assertNotIn('failed', result)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
