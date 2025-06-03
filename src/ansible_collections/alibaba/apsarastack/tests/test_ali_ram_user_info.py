# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import unittest

from dotenv import load_dotenv
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ram_user import main as ram_user_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ram_user_info import main as ram_user_info_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage


class Test(unittest.TestCase):

    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self.ram_user_args = {
                    "user_name": "ansiable_test_create_user",
                    "display_name": "ansiable-test-create-user",
                    "mobile_phone": "15111111111",
                    "email": "12345@qq.com",
                    "comments": "ansible_test"
                }

    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        load_dotenv()
        result = run_module(ram_user_main, self.ram_user_args)
        self.ram_user_args["user_id"] = result["user"]["primaryKey"]

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        self.ram_user_args["state"] = "absent"
        try:
            run_module(ram_user_main, self.ram_user_args)
        except:
            pass
    
    def testDescribeRamUser(self):
        user_ids_check = {
            "user_ids": [self.ram_user_args["user_id"]]
        }
        result = run_module(ram_user_info_main, user_ids_check)
        self.assertEqual(len(result["users"]), 1)
        self.assertEqual(result["users"][0]["primaryKey"], self.ram_user_args["user_id"])
        name_pre_check = {
            "name_prefix": self.ram_user_args["user_name"][:20]
        }
        result = run_module(ram_user_info_main, name_pre_check)
        user_names = [x["loginName"] for x in result["users"]]
        self.assertIn(self.ram_user_args["user_name"], user_names)

        display_name_pre_check = {
            "display_name_prefix": self.ram_user_args["display_name"][:20]
        }
        result = run_module(ram_user_info_main, display_name_pre_check)
        user_names = [x["displayName"] for x in result["users"]]
        self.assertIn(self.ram_user_args["display_name"], user_names)
        


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
