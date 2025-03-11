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

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        vpc_args = {
            "state": "absent",
        } | self._vpc_info
        try:
            run_module(vpc_main, vpc_args)
        except:
            pass

    def testCreateSecurityGroup(self):
        security_group_args = {
            "name": self.name,  
            "vpc_id": self._vpc_info['id']
        }
        result = run_module(security_group_main, security_group_args)
        self.assertNotIn('failed', result)
        self.assertEqual(result['changed'], False)
        self.assertEqual(result['group']['group_name'], security_group_args['name'])
        group_id = result['group']["group_id"]
        group_name = result['group']["group_name"]
        security_group_rules_args = {
            "name": self.name,  
            "vpc_id": self._vpc_info['id'],
            "rules":[
                {"ip_protocol": "tcp",
                 "port_range": "1/122",
                 "source_cidr_ip": "10.159.6.18/12"
                },
            ]
        }
        result = run_module(security_group_main, security_group_rules_args)
        self.assertNotIn('failed', result)
        self.assertEqual(result['changed'], True)
        self.assertEqual(result['group']['permissions'][0]["ip_protocol"].lower(), security_group_rules_args['rules'][0]["ip_protocol"].lower())
        self.assertEqual(result['group']['permissions'][0]["port_range"], security_group_rules_args['rules'][0]["port_range"])
        self.assertEqual(result['group']['permissions'][0]["source_cidr_ip"], security_group_rules_args['rules'][0]["source_cidr_ip"])

        security_group_args = {
            "state": "absent",
            "security_group_id": group_id,
            "name": group_name
        }
        result = run_module(security_group_main, security_group_args)
        self.assertNotIn('failed', result, result.get('msg', ''))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
