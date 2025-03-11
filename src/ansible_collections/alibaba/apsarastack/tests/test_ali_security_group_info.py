# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import unittest
import uuid
import sys


from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.plugins.modules.ali_security_group_info import main as security_group_info_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vpc import main as vpc_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_security_group import main as security_group_main

class Test(unittest.TestCase):

    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self.name = "New-vpcv%s" % uuid.uuid1()
        self._vpc_info = {
            "vpc_name": self.name,
            "cidr_block": "172.16.0.0/16",
            "description": "new_vpc",
        }
        self._security_group_info = {
            "name": self.name,
            "rules":[
                {"ip_protocol": "tcp",
                 "port_range": "1/122",
                 "source_cidr_ip": "10.159.6.18/12"
                },
            ]
        }

    def setUp(self)->None:
        unittest.TestCase.setUp(self)
        load_dotenv()
        vpc_args = self._vpc_info
        result = run_module(vpc_main, vpc_args)
        self._vpc_info['id'] = result['vpc']['vpc_id']
        self._security_group_info["vpc_id"] = self._vpc_info['id']
        security_group_rules_args = self._security_group_info
        result = run_module(security_group_main, security_group_rules_args)
        self._security_group_info["id"] = result["group"]["id"]

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        vpc_args = {
            "state": "absent",
        } | self._vpc_info
        security_group_args = {
            "state": "absent",
        } | self._security_group_info
        try:
            run_module(vpc_main, vpc_args)
            run_module(security_group_main, security_group_args)
        except:
            pass

    def testDescribediskInfo(self):        
        security_group_info_args = {
            "name_prefix": "New-vpcv",
        }
        result = run_module(security_group_info_main, security_group_info_args)
        self.assertEqual(len(result['groups']), 1,)
        self.assertEqual(result['groups'][0]['id'], self._security_group_info["id"])
        security_group_info_args = {
            "name_prefix": '_New-vpcv',
        }
        result = run_module(security_group_info_main, security_group_info_args)
        self.assertEqual(len(result['groups']), 0,)

        security_group_info_args = {
            "group_name": self.name,
        }
        result = run_module(security_group_info_main, security_group_info_args)
        self.assertEqual(len(result['groups']), 1,)
        self.assertEqual(result['groups'][0]['id'], self._security_group_info["id"])
        security_group_info_args = {
            "group_name": self.name + "__",
        }
        result = run_module(security_group_info_main, security_group_info_args)
        self.assertEqual(len(result['groups']), 0,)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreatedisk']
    run_unittest_with_coverage()
