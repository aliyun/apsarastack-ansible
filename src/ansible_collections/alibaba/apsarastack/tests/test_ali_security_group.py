# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import unittest
import sys
import uuid

from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.plugins.modules.ali_security_group import main as security_group_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vpc import main as vpc_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage


class Test(unittest.TestCase):


    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self.name = "ansible_test_security_group_info_%s" % uuid.uuid1()
        self._vpc_info = {
            "cidr_block": "172.16.0.0/16",
            "vpc_name": self.name,
            "description": "create by ansible unit test",
            "tags": {"key1":"value1"}
        }

    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        load_dotenv()
        vpc_args = self._vpc_info
        result = run_module(vpc_main, vpc_args)
        self._vpc_info['id'] = result['vpc']['vpc_id']

    def testCreateSecurityGroup(self):
        security_group_args = {
            "state": "absent",
            "name": self.name,
            "vpc_id": self._vpc_info['id']
        }
        result = run_module(security_group_main, security_group_args)
        self.assertNotIn('failed', result)
        self.assertEqual(result['changed'], False)
        self.assertEqual(result['group']['group_name'], security_group_args['name'])
        
        # vpc_args = {
        #     "state": "present",
        #     "cidr_block": "192.168.0.0/24",
        #     "vpc_name": "ansible_test_vpc",
        #     "description": "create by ansible unit test",
        # }
        # result = run_module(vpc_main, vpc_args)
        # self.assertNotIn('failed', result, result.get('msg', ''))
        # self.assertEqual(result['vpc']['vpc_name'], vpc_args['vpc_name'])
        
        # vpc_args = {
        #     "state": "present",
        #     "cidr_block": "192.168.0.0/24",
        #     "vpc_name": "ansible_test_vpc",
        #     "description": "modify by ansible unit test",
        # }
        # result = run_module(vpc_main, vpc_args)
        # self.assertNotIn('failed', result, result.get('msg', ''))
        # self.assertTrue(result['changed'])
        # self.assertEqual(result['vpc']['description'], vpc_args['description'])
        
        # vpc_args = {
        #     "state": "present",
        #     "cidr_block": "192.168.0.0/24",
        #     "vpc_name": "ansible_test_vpc",
        #     "description": "modify by ansible unit test",
        #     "tags": {"key1":"value1"}
        # }
        # result = run_module(vpc_main, vpc_args)
        # self.assertNotIn('failed', result, result.get('msg', ''))
        # self.assertTrue(result['changed'])
        # # TODO: 无法读取到tag信息
        
        # vpc_args = {
        #     "state": "present",
        #     "cidr_block": "192.168.0.0/24",
        #     "vpc_name": "ansible_test_vpc",
        #     "description": "modify by ansible unit test",
        #     "purge_tags": True
        # }
        # result = run_module(vpc_main, vpc_args)
        # self.assertNotIn('failed', result, result.get('msg', ''))
        # self.assertTrue(result['changed'])

        # vpc_args = {
        #     "state": "absent",
        #     "cidr_block": "192.168.0.0/24",
        #     "vpc_id": result['vpc']['vpc_id'],
        # }
        # result = run_module(vpc_main, vpc_args)
        # self.assertNotIn('failed', result, result.get('msg', ''))

        # vpc_args = {
        #     "cidr_block": "192.168.0.0/24",
        #     "vpc_name": "http://ansible_test_vpc",
        #     "description": "modify by ansible unit test",
        # }
        # result = run_module(vpc_main, vpc_args)
        # self.assertIn('failed', result)
        # self.assertEqual(result['msg'], 'vpc_name can not start with http:// or https://')
        
        # vpc_args = {
        #     "cidr_block": "192.168.0.0/24",
        #     "vpc_name": "ansible_test_vpc",
        #     "description": "http://modify by ansible unit test",
        # }
        # result = run_module(vpc_main, vpc_args)
        # self.assertIn('failed', result)
        # self.assertEqual(result['msg'], 'description can not start with http:// or https://')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
