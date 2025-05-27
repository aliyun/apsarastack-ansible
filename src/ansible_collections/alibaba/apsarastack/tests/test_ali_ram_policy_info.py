# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import unittest

from dotenv import load_dotenv
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ram_policy import main as ram_policy_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ram_policy_info import main as ram_policy_info_mains
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage


class Test(unittest.TestCase):

    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self.ram_policy_args = {
            "policy_name": "ansible-policy-test",
            "policy_document": "{\"Statement\":[{\"Action\":\"ecs:*\",\"Effect\":\"Allow\",\"Resource\":\"*\"}],\"Version\":\"1\"}",
            "description": "create for ansible"
        }

    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        load_dotenv()
        result = run_module(ram_policy_main, self.ram_policy_args)
        self.ram_policy_args["policy_id"] = result['policy']['id']

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        self.ram_policy_args["state"] = "absent"
        try:
            run_module(ram_policy_main, self.ram_policy_args)
        except:
            pass
    
    def testDescribeRamRole(self):
        name_pre_check = {
            "name_prefix": "ansible-policy-"
        }
        result = run_module(ram_policy_info_mains, name_pre_check)
        policy_names = [x["policyName"] for x in result["policies"]]
        self.assertIn(self.ram_policy_args["policy_name"], policy_names)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
