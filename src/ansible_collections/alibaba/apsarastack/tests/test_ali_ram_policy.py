# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ram_role import main as ram_role_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ram_policy import main as ram_policy_main
from dotenv import load_dotenv
import unittest


class Test(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self.ram_role_args = {
            "role_name": "ansiable-test-create-user",
            "role_range": "rawRamRole",
            "description": "ansiable_test_create_user",
            "assumerole_policydocument": {
                "Version": "1",
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Effect": "Allow",
                        "Principal": {
                            "Service": [
                                "rds.aliyuncs.com"
                            ],
                            "RAM": [
                                "acs:ram::1469947189201582:root"
                            ]
                        }
                    }
                ]
            }
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

    def testCreateRamPolicy(self):
        ram_policy_args = {
            "policy_name": "ansible-policy-test",
            "policy_document": "{\"Statement\":[{\"Action\":\"ecs:*\",\"Effect\":\"Allow\",\"Resource\":\"*\"}],\"Version\":\"1\"}",
            "description": "create for ansible"
        }
        result = run_module(ram_policy_main, ram_policy_args)
        self.assertEqual(result['policy']["policyName"],
                         ram_policy_args["policy_name"])
        self.assertEqual(result['policy']["policyDocument"],
                         ram_policy_args["policy_document"])
        ram_policy_args["policy_id"] = result['policy']['id']
        ram_policy_args["role_id"] = self.ram_role_args["role_id"]
        result = run_module(ram_policy_main, ram_policy_args)
        self.assertNotIn('failed', result)
        ram_policy_args["state"] = "absent"
        result = run_module(ram_policy_main, ram_policy_args)
        self.assertNotIn('failed', result)
        del ram_policy_args["role_id"]
        result = run_module(ram_policy_main, ram_policy_args)
        self.assertNotIn('failed', result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
