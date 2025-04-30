# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import unittest
import uuid
import time 

from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vpc import main as vpc_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vswitch import main as vswtich_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_slb_lb_info import main as slb_info_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_slb_lb import main as slb_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_security_group import main as security_group_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_instance import main as instance_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_slb_server import main as slb_server_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_slb_server_info import main as slb_server_info_main
from ansible_collections.alibaba.apsarastack.tests.utils import generate_password
class Test(unittest.TestCase):

    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self.name = "ansible_test_slb_server_info_%s" % uuid.uuid1()
        self.password = generate_password()
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
        "image": "aliyun_3_arm64_20G_pro_alibase_20240716.vhd",
        "instance_type": "ecs.g5s-ft-k10-c1m1.large",
        "instance_name": self.name,
        "password": self.password,
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
        self._slb_args = {
            "internet_charge_type": "PayByTraffic",
            "load_balancer_name": self.name,
            "load_balancer_spec": "slb.s1.small",
            "purge_tags": False,

        }

    def setUp(self)->None:
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
        self._slb_args["vswitch_id"] = self._vswtich_args["id"]
        result = run_module(slb_main, self._slb_args)
        self._slb_args["id"] = result["load_balancer"]["load_balancer_id"]
        self._slb_server_args = {
            "backend_servers": [
                {"server_id": self._ecs_instance_args["id"],
                 "weight": 80,
                 "port": 100
                 }
            ],
            "load_balancer_id": self._slb_args["id"]

        }
        run_module(slb_server_main, self._slb_server_args)

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        slb_server_args = {
            "state": "absent",
        } | self._slb_server_args
        run_module(slb_server_main, slb_server_args)
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
        slb_args = {
            "state": "absent",
        }| self._slb_args
        try:
            run_module(security_group_main, security_group)
        except:
            pass
        try:
            run_module(slb_main, slb_args)
            run_module(vswtich_main, vswitch)
            run_module(vpc_main, vpc_args)
        except:
            pass

    def testDescribeSlbInfo(self):
        slb_server_args = {
            "load_balancer_id": self._slb_args["id"],
        }
        result = run_module(slb_server_info_main, slb_server_args)
        self.assertEqual(result['load_balancer_id'], slb_server_args["load_balancer_id"],)

        


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
