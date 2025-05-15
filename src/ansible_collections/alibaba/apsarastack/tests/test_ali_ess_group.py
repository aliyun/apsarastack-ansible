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
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vpc import main as vpc_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vswitch import main as vswtich_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_rds_instance import main as rds_instance_main

class Test(unittest.TestCase):



    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self.name = "ansible_test_ess_group_%s" % uuid.uuid1()
        self._vpc_args = {
            "cidr_block": "192.168.0.0/16",
            "vpc_name": self.name,
            "description": "create by ansible unit test",
        }
        self._vswtich_args = {
            "cidr_block": "192.168.0.0/16",
            "name": self.name
        }
        self._rds_instance_args = {
        "engine": "MySQL",
        "engine_version": "5.7",
        "db_instance_class": "rds.mysql.t1.small",
        "instance_storage": "5",
        "db_instance_net_type": "Intranet",
        "connection_mode": "Standard",
        "security_ip_list": '192.168.1.0/16',
        "pay_type": "PostPaid",
        "db_instance_name": self.name
            }

    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        load_dotenv()
        result = run_module(vpc_main, self._vpc_args)
        self._vpc_args['id'] = result['vpc']['vpc_id']
        self._vswtich_args["vpc_id"] = result['vpc']['vpc_id']
        result = run_module(vswtich_main, self._vswtich_args)
        self._vswtich_args["id"] = result['vswitch']['vswitch_id']
        self._rds_instance_args["vswitch_id"] = result['vswitch']['vswitch_id']
        result = run_module(rds_instance_main, self._rds_instance_args)
        self._rds_instance_args["id"] = result['instances']['id']

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        rds_instance_args = {
            "state": "absent",
        }|self._rds_instance_args    
        vswitch = {
            "state": "absent",
        } | self._vswtich_args
        vpc_args = {
            "state": "absent",
        } | self._vpc_args
        try:
            run_module(rds_instance_main, rds_instance_args)
            run_module(vswtich_main, vswitch)
            run_module(vpc_main, vpc_args)
        except:
            pass
    def testCreateEssGroup(self):
        ess_group_args = {
            "state": "present",
            "name": self.name,
            "max_size": 100,
            "min_size": 1,
            "cooldown": 300,
            "removal_policies": ["OldestInstance", "NewestInstance"],
            "vswitch_ids": [self._vswtich_args["id"]],
            "vpc_id": self._vpc_args["id"],
            "db_instance_ids": [self._rds_instance_args["id"]]

        }
        result = run_module(ess_group_main, ess_group_args)
        self.assertEqual(result['name'], ess_group_args['name'])
        ess_group_args["state"] = "absent"
        result = run_module(ess_group_main, ess_group_args)
        self.assertNotIn('failed', result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
