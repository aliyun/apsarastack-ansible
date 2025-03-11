# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import unittest
import uuid

from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vpc import main as vpc_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vswitch import main as vswitch_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage


class Test(unittest.TestCase):

    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self._vpc_info = {
            "cidr_block": "172.16.0.0/16",
            "vpc_name": "ansible_test_vswtich",
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
        try:
            run_module(vpc_main, vpc_args)
        except:
            pass

    def testDescribeVpcInfo(self):
        
        vswtich_args = {
            "state": "absent",
            "cidr_block": "192.168.0.0/24",
            "vpc_id": self._vpc_info['id'],
            "id": 'not_exist_test',
        }
        result = run_module(vswitch_main, vswtich_args)
        self.assertNotIn('failed', result)
        self.assertFalse(result['changed'])
        self.assertEqual(result['vswitch'], {})

        vswtich_args = {
            "vpc_id": self._vpc_info['id'],
            "cidr_block": "172.16.1.0/24",
            "name": 'ansible_test_vswtich',
        }
        result = run_module(vswitch_main, vswtich_args)
        self.assertEqual(result['vswitch']['vpc_id'], self._vpc_info['id'])
        self.assertEqual(result['vswitch']['vswitch_name'], vswtich_args['name'])

        vswtich_args = {
            "vpc_id": self._vpc_info['id'],
            "id": result['vswitch']['id'],
            "cidr_block": "172.16.1.0/24",
            "name": 'modify_ansible_test_vswtich',
        }
        result = run_module(vswitch_main, vswtich_args)
        self.assertNotIn('failed', result, result.get('msg', ''))
        self.assertTrue(result['changed'])
        self.assertEqual(result['vswitch']['vswitch_name'], vswtich_args['name'])
        
        vswtich_args = {
            "vpc_id": self._vpc_info['id'],
            "id": result['vswitch']['id'],
            "cidr_block": "172.16.1.0/24",
            "tags": {"key1":"value1"}
        }
        result = run_module(vswitch_main, vswtich_args)
        self.assertNotIn('failed', result, result.get('msg', ''))
        self.assertTrue(result['changed'])
        # TODO: 无法读取到tag信息
        
        vswtich_args = {
            "vpc_id": self._vpc_info['id'],
            "id": result['vswitch']['id'],
            "cidr_block": "172.16.1.0/24",
            "purge_tags": True
        }
        result = run_module(vswitch_main, vswtich_args)
        self.assertNotIn('failed', result, result.get('msg', ''))
        self.assertTrue(result['changed'])

        vswtich_args = {
            "state": "absent",
            "id": result['vswitch']['id'],
            "vpc_id": self._vpc_info['id'],
            "cidr_block": "172.16.1.0/24",
            "name": 'ansible_test_vswtich',
        }
        result = run_module(vswitch_main, vswtich_args)
        self.assertNotIn('failed', result, result.get('msg', ''))

        vswtich_args = {
            "vpc_id": self._vpc_info['id'],
            "cidr_block": "172.16.1.0/24",
            "name": 'http://ansible_test_vswtich',
        }
        result = run_module(vswitch_main, vswtich_args)
        self.assertIn('failed', result)
        self.assertEqual(result['msg'], 'vswitch_name can not start with http:// or https://')

        vswtich_args = {
            "vpc_id": self._vpc_info['id'],
            "cidr_block": "172.16.1.0/24",
            "name": 'ansible_test_vswtich',
            "description": "http://modify by ansible unit test",
        }
        result = run_module(vswitch_main, vswtich_args)
        self.assertIn('failed', result)
        self.assertEqual(result['msg'], 'description can not start with http:// or https://')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
