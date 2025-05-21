# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import uuid
import unittest
import time
from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ess_group import main as ess_group_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ess_instance import main as ess_instance_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vpc import main as vpc_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vswitch import main as vswtich_main
from ansible_collections.alibaba.apsarastack.tests.utils import generate_password
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_security_group import main as security_group_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_instance import main as instance_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ess_configuration import main as ess_configuration_main

class Test(unittest.TestCase):



    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self.name = "ansible_test_ess_instance_%s" % uuid.uuid1()
        self.passward = generate_password()
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
        self._ecs_args = {
        "state": 'present',
        "image": "aliyun_3_arm64_20G_pro_alibase_20240716.vhd",
        "instance_type": "ecs.g5s-ft-k10.customize.xgzapwqomq",
        "instance_name": self.name,
        "password": self.passward,
        "count_tag": '{"test": "test"}',
        "tags": {
            "test": "test"
        },
        "count": 1,
        "system_disk_name": "ansible_test_ecs_instance_test",
        "system_disk_category": "cloud_ssd",
        "max_bandwidth_out": "10",
        "system_disk_size": "20",
        "instance_charge_type": "PostPaid",
        "internet_charge_type": "PayByTraffic",
        "allocate_public_ip": True,
        "force": True,
            }
        self.ess_group_args = {
            "state": "present",
            "name": self.name,
            "max_size": 20,
            "min_size": 0,
            "cooldown": 20,
            "removal_policies": ["OldestInstance", "NewestInstance"]

        }
        self._ess_configuration = {
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
        self._ecs_args["vswitch_id"] = self._vswtich_args["id"]
        self._ecs_args["security_groups"] = [self._security_group_args["id"],]
        result = run_module(instance_main, self._ecs_args)
        self._ecs_args["id"] = result['instances'][0]["id"]
        self.ess_group_args["vswitch_ids"] = [self._vswtich_args["id"]]
        self.ess_group_args["vpc_id"] = self._vpc_args["id"]
        result = run_module(ess_group_main, self.ess_group_args)
        self.ess_group_args["id"] = result["id"]
        self._ess_group_id = result['id']
        self._ess_configuration["group_id"] = self._ess_group_id
        self._ess_configuration["security_group_id"] = self._security_group_args["id"]
        result = run_module(ess_configuration_main, self._ess_configuration)
        self.ess_group_args["configuration_id"] = result["id"]
        self.ess_group_args["state"] = "active"
        run_module(ess_group_main, self.ess_group_args)

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        try:
            self.ess_group_args["state"] = "absent"
            run_module(ess_group_main, self.ess_group_args)
            vswitch = {
                "state": "absent",
            } | self._vswtich_args
            vpc_args = {
                "state": "absent",
            } | self._vpc_args
            self.ess_group_args["state"] = "absent"
            self._ecs_args["state"] = "absent"
            ecs_instance_args = {
                "state": "stopped",
                "force": True,
                "instance_ids": [self._ecs_args["id"]]
            }
            run_module(instance_main, ecs_instance_args)
            
            ecs_instance_args = {
                "state": "absent",
                "force": True,
                "instance_ids": [self._ecs_args["id"]]
            }
            for _ in range(12):
                result = run_module(instance_main, ecs_instance_args)
                if "failed" not in result:
                    break
                time.sleep(5)
            
            security_group = {
                "state": "absent",
            } | self._security_group_args
            time.sleep(10)
            run_module(security_group_main, security_group)
            run_module(vswtich_main, vswitch)
            run_module(vpc_main, vpc_args)
        except:
            pass

    def testCreateEssinstance(self):

        ess_instance_args = {
            "group_id": self._ess_group_id,
            "instance_ids": [self._ecs_args["id"]],
            "creation_type": "Attached"
        
        }
        result = run_module(ess_instance_main, ess_instance_args)
        self.assertEqual(set(ess_instance_args["instance_ids"]) - set([x["instance_id"] for x in result["changed"]]), set())
        ess_instance_args["state"] = "absent"
        result = run_module(ess_instance_main, ess_instance_args)
        self.assertEqual(set(ess_instance_args["instance_ids"]) - set([x["instance_id"] for x in result["changed"]]), set(ess_instance_args["instance_ids"]))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
