# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import unittest
import uuid

from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vpc import main as vpc_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vpc_info import main as vpc_info_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage


class Test(unittest.TestCase):

    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self._vpc_info = {
            "cidr_block": "192.168.0.0/24",
            "vpc_name": "ansible_test_vpc_info_%s" % uuid.uuid1(),
            "description": "create by ansible unit test",
            "tags": {"key1":"value1"}
        }

    def setUp(self)->None:
        unittest.TestCase.setUp(self)
        load_dotenv()
        vpc_args = self._vpc_info
        result = run_module(vpc_main, vpc_args)
        self._vpc_info['id'] = result['vpc']['vpc_id']

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        vpc_args = {
            "state": "absent",
        } | self._vpc_info
        run_module(vpc_main, vpc_args)

    def testDescribeVpcInfo(self):
        vpc_info_args = {
            "vpc_ids": self._vpc_info['id'],
        }
        result = run_module(vpc_info_main, vpc_info_args)
        self.assertEqual(len(result['vpcs']), 1,)
        self.assertEqual(result['vpcs'][0]['id'], self._vpc_info['id'])
        vpc_info_args = {
            "vpc_ids": self._vpc_info['id'] + "_",
        }
        result = run_module(vpc_info_main, vpc_info_args)
        self.assertEqual(len(result['vpcs']), 0,)

        vpc_info_args = {
            "vpc_name": self._vpc_info['vpc_name'],
        }
        result = run_module(vpc_info_main, vpc_info_args)
        self.assertEqual(len(result['vpcs']), 1,)
        self.assertEqual(result['vpcs'][0]['id'], self._vpc_info['id'])
        vpc_info_args = {
            "vpc_name": self._vpc_info['vpc_name'] + "_",
        }
        result = run_module(vpc_info_main, vpc_info_args)
        self.assertEqual(len(result['vpcs']), 0,)
        
        vpc_info_args = {
            "name_prefix": 'ansible_test_vpc_info_',
        }
        result = run_module(vpc_info_main, vpc_info_args)
        self.assertEqual(len(result['vpcs']), 1,)
        self.assertEqual(result['vpcs'][0]['id'], self._vpc_info['id'])
        vpc_info_args = {
            "name_prefix": '_ansible_test_vpc_info',
        }
        result = run_module(vpc_info_main, vpc_info_args)
        self.assertEqual(len(result['vpcs']), 0,)
        
        vpc_info_args = {
            "cidr_prefix": self._vpc_info['cidr_block'],
        }
        result = run_module(vpc_info_main, vpc_info_args)
        self.assertEqual(len(result['vpcs']), 1,)
        self.assertEqual(result['vpcs'][0]['id'], self._vpc_info['id'])
        vpc_info_args = {
            "cidr_prefix": '10.0.0.1/8',
        }
        result = run_module(vpc_info_main, vpc_info_args)
        self.assertEqual(len(result['vpcs']), 0,)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
