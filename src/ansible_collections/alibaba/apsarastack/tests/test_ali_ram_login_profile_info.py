# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import unittest


from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ram_login_profile import main as ram_login_profile_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ram_login_profile_info import main as ram_login_profile_info_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage


class Test(unittest.TestCase):

    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self.ram_login_prifile_args = {
            "name": "ansiable-test-pre",
            "organization_visibility": "global",
            "description": "ansiable-test-pre",
            "rule": "deny"
        }
    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        load_dotenv()
        result = run_module(ram_login_profile_main, self.ram_login_prifile_args)
        self.ram_login_prifile_args["id"] = result['profile']["id"]

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        self.ram_login_prifile_args["state"] = "absent"
        try:
            run_module(ram_login_profile_main, self.ram_login_prifile_args)
        except:
            pass
    
    def testDescribeRamLoginPolicy(self):
        name_pre_check = {
            "user_name": "ansiable-test-"
        }
        result = run_module(ram_login_profile_info_main, name_pre_check)
        self.assertEqual(len(result["profile"]), 1)
        self.assertEqual(result["profile"][0]["id"], self.ram_login_prifile_args["id"])
        user_names = [x["name"] for x in result["profile"]]
        self.assertIn(self.ram_login_prifile_args["name"], user_names)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
