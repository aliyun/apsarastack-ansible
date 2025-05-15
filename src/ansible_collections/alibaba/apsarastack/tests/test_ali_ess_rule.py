# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import uuid
import unittest
from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ess_group import main as ess_group_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ess_rule import main as ess_rule_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vpc import main as vpc_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vswitch import main as vswtich_main

class Test(unittest.TestCase):



    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self.name = "ansible_test_ess_rule_%s" % uuid.uuid1()
        self._vpc_args = {
            "cidr_block": "172.16.0.0/16",
            "vpc_name": self.name,
            "description": "create by ansible unit test",
        }
        self._vswtich_args = {
            "cidr_block": "172.16.1.0/24",
            "name": self.name
        }
        self.ess_group_args = {
            "state": "present",
            "name": self.name,
            "max_size": 100,
            "min_size": 1,
            "cooldown": 300,
            "removal_policies": ["OldestInstance", "NewestInstance"]

        }

    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        load_dotenv()
        result = run_module(vpc_main, self._vpc_args)
        self._vpc_args['id'] = result['vpc']['vpc_id']
        self._vswtich_args["vpc_id"] = result['vpc']['vpc_id']
        result = run_module(vswtich_main, self._vswtich_args)
        self._vswtich_args["id"] = result['vswitch']['vswitch_id']
        self.ess_group_args["vswitch_ids"] = [self._vswtich_args["id"]]
        self.ess_group_args["vpc_id"] = self._vpc_args["id"]
        result = run_module(ess_group_main, self.ess_group_args)
        self._ess_group_id = result['id']

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        vswitch = {
            "state": "absent",
        } | self._vswtich_args
        vpc_args = {
            "state": "absent",
        } | self._vpc_args
        ess_group_args = {
            "state": "absent",
        } | self.ess_group_args
        try:
            run_module(ess_group_main, ess_group_args)
            run_module(vswtich_main, vswitch)
            run_module(vpc_main, vpc_args)
        except:
            pass

    def testCreateEssrule(self):
        ess_rule_args = {
            "state": "present",
            "name": self.name,
            "adjustment_type": "QuantityChangeInCapacity",
            "adjustment_value": 10,
            "cooldown": 60,
            "group_id": self._ess_group_id

        }
        result = run_module(ess_rule_main, ess_rule_args)
        self.assertEqual(result['name'], ess_rule_args['name'])
        ess_rule_args["adjustment_type"] = "PercentChangeInCapacity"
        ess_rule_args["value"] = 20
        result = run_module(ess_rule_main, ess_rule_args)
        self.assertEqual(result['rule']["adjustment_type"], ess_rule_args["adjustment_type"])
        self.assertEqual(result['rule']["adjustment_value"], ess_rule_args["value"])
        ess_rule_args["state"] = "absent"
        result = run_module(ess_rule_main, ess_rule_args)
        self.assertNotIn('failed', result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
