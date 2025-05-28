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
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ram_group import main as ram_group_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ram_group_info import main as ram_group_info_main

class Test(unittest.TestCase):

    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self.name = "ansiable-test-create-user-group"
        self.ram_user_group = {
            "group_name": self.name
        }

    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        load_dotenv()
        result = run_module(ram_group_main, self.ram_user_group)
        self.ram_user_group["group_id"] = result["group"]["id"]

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        self.ram_user_group["state"] = "absent"
        try:
            run_module(ram_group_main, self.ram_user_group)
        except:
            pass
    
    def testDescribeRamRole(self):
        name_pre_check = {
            "name_prefix": "ansiable-test-create-user"
        }
        result = run_module(ram_group_info_main, name_pre_check)
        groups = [x["groupName"] for x in result["groups"]]
        self.assertIn(self.ram_user_group["group_name"], groups)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
