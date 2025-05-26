# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import unittest


from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ram_role import main as ram_role_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage


class Test(unittest.TestCase):

    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        load_dotenv()
    
    def testCreateRole(self):
        ram_role_args = {
            "role_name": "ansiable-test-create-user",
            "role_range": "orgAndSubOrgs",
            "description": "ansiable_test_create_user"
        }
        result = run_module(ram_role_main, ram_role_args)
        self.assertEqual(result['role']["roleName"], ram_role_args["role_name"])
        self.assertEqual(result['role']["roleRange"], "roleRange." +ram_role_args["role_range"])
        self.assertEqual(result['role']["description"], ram_role_args["description"])
        update_ram_role_args = {
            "role_id": result["role"]["id"],
            "role_name": "ansiable-test-create-user-change",
            "role_range": "resourceSet",
            "description": "ansiable_test_create_user_update_change"
        }
        result = run_module(ram_role_main, update_ram_role_args)
        self.assertEqual(result['role']["roleName"], update_ram_role_args["role_name"])
        self.assertEqual(result['role']["roleRange"], "roleRange." +update_ram_role_args["role_range"])
        self.assertEqual(result['role']["description"], update_ram_role_args["description"])
        update_ram_role_args["state"] = "absent"
        result = run_module(ram_role_main, update_ram_role_args)
        self.assertNotIn('failed', result)
        


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
