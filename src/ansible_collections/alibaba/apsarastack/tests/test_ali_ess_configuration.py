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
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ess_configuration import main as ess_configuration_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vpc import main as vpc_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vswitch import main as vswtich_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_security_group import main as security_group_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_instance import main as instance_main

class Test(unittest.TestCase):



    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self.name = "ansible_test_ess_%s" % uuid.uuid1()
        self._vpc_args = {
            "cidr_block": "172.16.0.0/16",
            "vpc_name": self.name,
            "description": "create by ansible unit test",
        }
        self._vswtich_args = {
            "cidr_block": "172.16.1.0/24",
            "name": self.name
        }
        self._security_group_args = {
            "name": self.name
        }
        self.ess_group_args = {
            "state": "present",
            "name": self.name,
            "max_size": 20,
            "min_size": 0,
            "cooldown": 20,
            "removal_policies": ["OldestInstance", "NewestInstance"]

        }

    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        load_dotenv()
        result = run_module(vpc_main, self._vpc_args)
        self._vpc_args['id'] = result['vpc']['vpc_id']
        self._vswtich_args["vpc_id"] = result['vpc']['vpc_id']
        self._security_group_args["vpc_id"] = result['vpc']['vpc_id']
        result = run_module(vswtich_main, self._vswtich_args)
        self._vswtich_args["id"] = result['vswitch']['vswitch_id']
        result = run_module(security_group_main, self._security_group_args)
        self._security_group_args["id"] = result['group']["group_id"]
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
        security_group = {
            "state": "absent",
        } | self._security_group_args
        try:
            run_module(ess_group_main, ess_group_args)
            run_module(security_group_main, security_group)
            run_module(vswtich_main, vswitch)
            run_module(vpc_main, vpc_args)
        except:
            pass

    def testCreateEssConfiguration(self):

        ess_configuration_args = {
        "group_id" : self._ess_group_id,
        "instance_type": "ecs.g5s-ft-k10.customize.xgzapwqomq",
        "image_id": "aliyun_3_arm64_20G_pro_alibase_20240716.vhd",
        "name": "ansiable_test",
        "internet_charge_type":"PayByBandwidth",
        "max_bandwidth_in": 200,
        "max_bandwidth_out":0,
        "system_disk_category":"cloud_ssd",
        "system_disk_size":20,
        "tags":{
            "test": "test"
        },
        "key_name":"",
        "user_data":"",
        "data_disks": [],
        "security_group_id": self._security_group_args["id"]

        }
        result = run_module(ess_configuration_main, ess_configuration_args)
        self.assertEqual(result['changed'], False)
        self.assertEqual(result['name'], ess_configuration_args["name"])
        ess_configuration_args["state"] = "absent"
        result = run_module(ess_configuration_main, ess_configuration_args)
        self.assertNotIn('failed', result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
