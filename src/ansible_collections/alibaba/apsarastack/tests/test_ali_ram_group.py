# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import unittest


from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ram_user import main as ram_user_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ram_role import main as ram_role_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ram_group import main as ram_group_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage


class Test(unittest.TestCase):

    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self.name = "ansiable-test-create-user-group"
        self.ram_user_args = {
            "user_name": self.name,
            "display_name": self.name,
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
    
    def testCreateRamGroup(self):
        ram_user_group = {
            "group_name": self.name
        }
        result = run_module(ram_group_main, ram_user_group)
        self.assertEqual(result['group']["groupName"], ram_user_group["group_name"])
        ram_user_group["group_id"] = result["group"]["id"]

        ram_user_group = {'group_name': self.name, 'user_name': self.name}
        result = run_module(ram_group_main, ram_user_group)
        self.assertIn(ram_user_group["user_name"], [x["username"] for x in result["group"]["users"]])

        
        ram_user_group = {
            "state": "absent",
            "group_name": self.name,
            "user_name": self.name
        }
        result = run_module(ram_group_main, ram_user_group)
        flag = False
        if "users" in result["group"]:
            if ram_user_group["user_name"] not in [x["username"] for x in result["group"]["users"]]:
                flag = True
        else:
            flag = True
        self.assertTrue(flag)

        ram_user_group = {
            "state": "absent",
            "group_name": self.name,
        }
        result = run_module(ram_group_main, ram_user_group)
        self.assertNotIn('failed', result)

        


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
