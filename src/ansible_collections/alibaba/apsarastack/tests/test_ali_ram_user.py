# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import unittest



from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ram_user import main as ram_user_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage


class Test(unittest.TestCase):

    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        load_dotenv()
    
    def testCreateRamUser(self):
        ram_user_args = {
            "user_name": "ansiable_test_create_user",
            "display_name": "ansiable-test-create-user",
            "mobile_phone": "15111111111",
            "email": "12345@qq.com",
            "comments": "ansible_test"
        }
        result = run_module(ram_user_main, ram_user_args)
        self.assertEqual(result['user']["displayName"], ram_user_args["display_name"])
        self.assertEqual(result['user']["cellphoneNum"], ram_user_args["mobile_phone"])
        ram_user_args["user_id"] = result["user"]["primaryKey"]
        ram_user_args["display_name"] = "ansiable-test-change"
        ram_user_args["mobile_phone"] = "15122222222"
        result = run_module(ram_user_main, ram_user_args)
        self.assertEqual(result['user']["displayName"], ram_user_args["display_name"])
        self.assertEqual(result['user']["cellphoneNum"], ram_user_args["mobile_phone"])
        ram_user_args["state"] = "absent"
        result = run_module(ram_user_main, ram_user_args)
        self.assertNotIn('failed', result)
        


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
