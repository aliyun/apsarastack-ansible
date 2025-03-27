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

    def testDescribeSlbInfo(self):
        slb_args = {
            "load_balancer_name": [self.name],
        }
        result = run_module(slb_info_main, slb_args)
        self.assertEqual(len(result['load_balancers']), 1,)
        self.assertEqual(result['load_balancers'][0]['load_balancer_name'], self.name)
        slb_args = {
            "load_balancer_ids": [self._slb_args["id"]],
        }
        result = run_module(slb_info_main, slb_args)
        self.assertEqual(len(result['load_balancers']), 1,)
        self.assertEqual(result['load_balancers'][0]['id'], slb_args["load_balancer_ids"][0])

        slb_args = {
            "name_prefix": "ansible_test_slb_info_",
        }
        result = run_module(slb_info_main, slb_args)
        self.assertEqual(len(result['load_balancers']), 1,)
        self.assertEqual(result['load_balancers'][0]['load_balancer_name'], self.name)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
