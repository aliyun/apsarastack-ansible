# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import unittest

from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ram_role import main as ram_role_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ram_role_info import main as ram_role_info_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage


class Test(unittest.TestCase):

    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self.ram_role_args = {
            "role_name": "ansiable-test-create-user",
            "role_range": "orgAndSubOrgs",
            "description": "ansiable_test_create_user"
        }

    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        load_dotenv()
        result = run_module(ram_role_main, self.ram_role_args)
        self.ram_role_args["role_id"] = result["role"]["id"]

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        self.ram_role_args["state"] = "absent"
        try:
            run_module(ram_role_main, self.ram_role_args)
        except:
            pass
    
    def testDescribeRamRole(self):
        name_pre_check = {
            "name_prefix": "ansiable-test-create-"
        }
        result = run_module(ram_role_info_main, name_pre_check)
        self.assertEqual(len(result["roles"]), 1)
        self.assertEqual(result["roles"][0]["id"], self.ram_role_args["role_id"])
        user_names = [x["roleName"] for x in result["roles"]]
        self.assertIn(self.ram_role_args["role_name"], user_names)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
