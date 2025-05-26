# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import unittest


from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ram_login_profile import main as ram_login_profile_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage


class Test(unittest.TestCase):

    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        load_dotenv()
    
    def testCreateRamLoginProfile(self):
        ram_login_prifile_args = {
            "name": "ansiable-test",
            "organization_visibility": "global",
            "description": "ld_test",
            "rule": "deny"
        }
        result = run_module(ram_login_profile_main, ram_login_prifile_args)
        self.assertEqual(result['profile']["name"], ram_login_prifile_args["name"])
        self.assertEqual(result['profile']["description"], ram_login_prifile_args["description"])
        self.assertEqual(result['profile']["rule"].lower(), ram_login_prifile_args["rule"])
        self.assertEqual(result['profile']["organizationVisibility"], "organizationVisibility." + ram_login_prifile_args["organization_visibility"])
        ram_login_prifile_modify = {
            "id": result['profile']["id"],
            "name": "ansiable-test-update",
            "description": "ansiable-test-update",
            "rule": "deny"
        }
        result = run_module(ram_login_profile_main, ram_login_prifile_modify)
        self.assertEqual(result['profile']["name"], ram_login_prifile_modify["name"])
        self.assertEqual(result['profile']["description"], ram_login_prifile_modify["description"])
        self.assertEqual(result['profile']["rule"].lower(), ram_login_prifile_modify["rule"])
        self.assertEqual(result['profile']["organizationVisibility"], "organizationVisibility." + ram_login_prifile_args["organization_visibility"])
        ram_login_prifile_modify["state"] = "absent"
        result = run_module(ram_login_profile_main, ram_login_prifile_modify)
        self.assertNotIn('failed', result)
        


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
