# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import unittest

from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vpc import main as vpc_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage


class Test(unittest.TestCase):

    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        load_dotenv()

    def testCreateVpc(self):
        vpc_args = {
            "state": "absent",
            "cidr_block": "192.168.0.0/24",
            "vpc_id": 'not_exist_test',
        }
        result = run_module(vpc_main, vpc_args)
        self.assertNotIn('failed', result)
        self.assertFalse(result['changed'])
        self.assertEqual(result['vpc'], {})
        
        vpc_args = {
            "state": "present",
            "cidr_block": "192.168.0.0/24",
            "vpc_name": "ansible_test_vpc",
            "description": "create by ansible unit test",
        }
        result = run_module(vpc_main, vpc_args)
        self.assertNotIn('failed', result, result.get('msg', ''))
        self.assertEqual(result['vpc']['vpc_name'], vpc_args['vpc_name'])
        
        vpc_args = {
            "state": "present",
            "cidr_block": "192.168.0.0/24",
            "vpc_name": "ansible_test_vpc",
            "description": "modify by ansible unit test",
        }
        result = run_module(vpc_main, vpc_args)
        self.assertNotIn('failed', result, result.get('msg', ''))
        self.assertTrue(result['changed'])
        self.assertEqual(result['vpc']['description'], vpc_args['description'])
        
        vpc_args = {
            "state": "present",
            "cidr_block": "192.168.0.0/24",
            "vpc_name": "ansible_test_vpc",
            "description": "modify by ansible unit test",
            "tags": {"key1":"value1"}
        }
        result = run_module(vpc_main, vpc_args)
        self.assertNotIn('failed', result, result.get('msg', ''))
        self.assertTrue(result['changed'])
        # TODO: 无法读取到tag信息
        
        vpc_args = {
            "state": "present",
            "cidr_block": "192.168.0.0/24",
            "vpc_name": "ansible_test_vpc",
            "description": "modify by ansible unit test",
            "purge_tags": True
        }
        result = run_module(vpc_main, vpc_args)
        self.assertNotIn('failed', result, result.get('msg', ''))
        self.assertTrue(result['changed'])

        vpc_args = {
            "state": "absent",
            "cidr_block": "192.168.0.0/24",
            "vpc_id": result['vpc']['vpc_id'],
        }
        result = run_module(vpc_main, vpc_args)
        self.assertNotIn('failed', result, result.get('msg', ''))

        vpc_args = {
            "cidr_block": "192.168.0.0/24",
            "vpc_name": "http://ansible_test_vpc",
            "description": "modify by ansible unit test",
        }
        result = run_module(vpc_main, vpc_args)
        self.assertIn('failed', result)
        self.assertEqual(result['msg'], 'vpc_name can not start with http:// or https://')
        
        vpc_args = {
            "cidr_block": "192.168.0.0/24",
            "vpc_name": "ansible_test_vpc",
            "description": "http://modify by ansible unit test",
        }
        result = run_module(vpc_main, vpc_args)
        self.assertIn('failed', result)
        self.assertEqual(result['msg'], 'description can not start with http:// or https://')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
