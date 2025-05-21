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
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ess_task import main as ess_task_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vpc import main as vpc_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vswitch import main as vswtich_main
from datetime import datetime, timedelta, timezone


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
            "name": self.name,
            "max_size": 100,
            "min_size": 0,
            "cooldown": 300,
            "removal_policies": ["OldestInstance", "NewestInstance"]

        }
        self.ess_rule_args = {
            "name": self.name,
            "adjustment_type": "QuantityChangeInCapacity",
            "adjustment_value": 10,
            "cooldown": 60,
            # "group_id": self._ess_group_id

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
        self.ess_group_args["id"] = result["id"]
        self.ess_rule_args["group_id"] = self._ess_group_id
        result = run_module(ess_rule_main, self.ess_rule_args)
        self.ess_rule_args["id"] = result["id"]


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
        self.ess_rule_args["state"] = "absent"
        try:
            run_module(ess_rule_main, self.ess_rule_args)
            run_module(ess_group_main, ess_group_args)
            run_module(vswtich_main, vswitch)
            run_module(vpc_main, vpc_args)
        except:
            pass

    def testCreateEssrule(self):
        # 获取当前 UTC 时间
        now = datetime.now(timezone.utc)
        future = now + timedelta(hours=9)
        recurrence_future = now + timedelta(days=10)
        launch_time = future.isoformat(timespec='minutes').replace('+00:00', 'Z')
        recurrence_endtime = recurrence_future.isoformat(timespec='minutes').replace('+00:00', 'Z')
        ess_task_args = {
            "launch_time": launch_time,
            "name": self.name,
            "description": self.name,
            "recurrence_type": "Daily",
            "recurrence_value": "2",
            "recurrence_endtime": recurrence_endtime,
            "rule_id": self.ess_rule_args["id"]
        }
        result = run_module(ess_task_main, ess_task_args)
        ess_task_args["id"] = result["task"]["id"]
        self.assertEqual(result["task"]["name"], ess_task_args["name"])
        ess_task_args["state"] = "absent"
        result = run_module(ess_task_main, ess_task_args)
        self.assertNotIn('failed', result)

        


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
