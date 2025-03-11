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
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vswitch_info import main as vswtich_info_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage


class Test(unittest.TestCase):

    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        name = "ansible_test_vswtich_info_%s" % uuid.uuid1()
        self._vpc_info = {
            "cidr_block": "172.16.0.0/16",
            "vpc_name": name,
            "description": "create by ansible unit test",
            "tags": {"key1":"value1"}
        }
        self._vswtich_info = {
            "cidr_block": "172.16.1.0/24",
            "name": name,
            "tags": {"key1":"value1"}
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

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        vswtich_args = {
            "state": "absent",
        } | self._vswtich_info
        run_module(vswtich_main, vswtich_args)
        vpc_args = {
            "state": "absent",
        } | self._vpc_info
        run_module(vpc_main, vpc_args)

    def testDescribeVpcInfo(self):
        vswtich_args = {
            "vswitch_ids": self._vswtich_info['id'],
        }
        result = run_module(vswtich_info_main, vswtich_args)
        self.assertEqual(len(result['vswitches']), 1,)
        self.assertEqual(result['vswitches'][0]['id'], self._vswtich_info['id'])
        vswtich_args = {
            "vswitch_ids": self._vswtich_info['id'] + "_",
        }
        result = run_module(vswtich_info_main, vswtich_args)
        self.assertEqual(len(result['vswitches']), 0,)

        vswtich_args = {
            "vswitch_name": self._vswtich_info['name'],
        }
        result = run_module(vswtich_info_main, vswtich_args)
        self.assertEqual(len(result['vswitches']), 1,)
        self.assertEqual(result['vswitches'][0]['id'], self._vswtich_info['id'])
        vswtich_args = {
            "vswitch_name": self._vswtich_info['name'] + "_",
        }
        result = run_module(vswtich_info_main, vswtich_args)
        self.assertEqual(len(result['vswitches']), 0,)
        
        vswtich_args = {
            "name_prefix": 'ansible_test_vswtich_info_',
        }
        result = run_module(vswtich_info_main, vswtich_args)
        self.assertEqual(len(result['vswitches']), 1,)
        self.assertEqual(result['vswitches'][0]['id'], self._vswtich_info['id'])
        vswtich_args = {
            "name_prefix": '_ansible_test_vswtich_info',
        }
        result = run_module(vswtich_info_main, vswtich_args)
        self.assertEqual(len(result['vswitches']), 0,)
        
        vswtich_args = {
            "cidr_block": self._vswtich_info['cidr_block'],
        }
        result = run_module(vswtich_info_main, vswtich_args)
        self.assertEqual(len(result['vswitches']), 1,)
        self.assertEqual(result['vswitches'][0]['id'], self._vswtich_info['id'])
        vswtich_args = {
            "cidr_block": '10.0.0.1/8',
        }
        result = run_module(vswtich_info_main, vswtich_args)
        self.assertEqual(len(result['vswitches']), 0,)
        
        vswtich_args = {
            "cidr_prefix": self._vswtich_info['cidr_block'],
        }
        result = run_module(vswtich_info_main, vswtich_args)
        self.assertEqual(len(result['vswitches']), 1,)
        self.assertEqual(result['vswitches'][0]['id'], self._vswtich_info['id'])
        vswtich_args = {
            "cidr_prefix": '10.0.0.1/8',
        }
        result = run_module(vswtich_info_main, vswtich_args)
        self.assertEqual(len(result['vswitches']), 0,)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
