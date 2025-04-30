# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import uuid
import unittest
import time


from dotenv import load_dotenv


from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vpc import main as vpc_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vswitch import main as vswtich_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_security_group import main as security_group_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_instance import main as instance_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_instance_info import main as instance_info_main
from ansible_collections.alibaba.apsarastack.tests.utils import generate_password
class Test(unittest.TestCase):

    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self.name = "ansible_test_ecs_instance_info_%s" % uuid.uuid1()
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
        self._ecs_instance_args = {
        "state": 'present',
        "image": "ubuntu_24_04_x86_64_20G_alibase_20241115.vhd",
        "instance_type": "ecs.xn4v2.small",
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
        self._ecs_instance_args["vswitch_id"] = self._vswtich_args["id"]
        self._ecs_instance_args["security_groups"] = [self._security_group_args["id"]]
        result = run_module(instance_main, self._ecs_instance_args)
        self._ecs_instance_args["id"] = result["instances"][0]["id"]

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        ecs_instance_args = {
            "state": "stopped",
            "force": True,
            "user_data": "ansible_test",
            "instance_ids": [self._ecs_instance_args["id"]]
        }
        run_module(instance_main, ecs_instance_args)
        
        ecs_instance_args = {
            "state": "absent",
            "force": True,
            "instance_ids": [self._ecs_instance_args["id"]]
        }
        for _ in range(12):
            result = run_module(instance_main, ecs_instance_args)
            if "failed" not in result:
                break
            time.sleep(5)
        
        security_group = {
            "state": "absent",
        } | self._security_group_args
        vswitch = {
            "state": "absent",
        } | self._vswtich_args
        vpc_args = {
            "state": "absent",
        } | self._vpc_args
        try:
            run_module(security_group_main, security_group)
        except:
            pass
        try:
            run_module(vswtich_main, vswitch)
            run_module(vpc_main, vpc_args)
        except:
            pass


    def testDescribeInstance(self):
        describe_instance_args = {
            "instance_names": [self.name]
            }
        result = run_module(instance_info_main, describe_instance_args)
        self.assertEqual(len(result["instances"]), 1)
        self.assertEqual(result["instances"][0]["instance_name"], self.name)

        describe_instance_args = {
            "instance_ids": [self._ecs_instance_args["id"]]
            }
        result = run_module(instance_info_main, describe_instance_args)
        self.assertEqual(len(result["instances"]), 1)
        self.assertEqual(result["instances"][0]["instance_id"], self._ecs_instance_args["id"])

        describe_instance_args = {
            "name_prefix": "ansible_test_ecs_instance_info"
            }
        result = run_module(instance_info_main, describe_instance_args)
        self.assertIn(self.name, [x["instance_name"] for x in result["instances"]])

        describe_instance_args = {
            "name_prefix": "fix_ansible_test_ecs_instance_info"
            }
        result = run_module(instance_info_main, describe_instance_args)
        self.assertNotIn(self.name, [x["instance_name"] for x in result["instances"]])
        
        
        


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
