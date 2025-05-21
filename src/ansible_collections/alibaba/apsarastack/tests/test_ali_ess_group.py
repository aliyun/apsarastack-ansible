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
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vpc import main as vpc_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vswitch import main as vswtich_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_rds_instance import main as rds_instance_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_security_group import main as security_group_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ess_configuration import main as ess_configuration_main
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
        self._security_group_args = {
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
        self._rds_instance_args["vswitch_id"] = result['vswitch']['vswitch_id']
        result = run_module(rds_instance_main, self._rds_instance_args)
        self._rds_instance_args["id"] = result['instances']['id']
        result = run_module(security_group_main, self._security_group_args)
        self._security_group_args["id"] = result['group']["group_id"]

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
            "min_size": 0,
            "cooldown": 300,
            "removal_policies": ["OldestInstance", "NewestInstance"],
            "vswitch_ids": [self._vswtich_args["id"]],
            "vpc_id": self._vpc_args["id"],
            "db_instance_ids": [self._rds_instance_args["id"]]

        }
        result = run_module(ess_group_main, ess_group_args)
        self.assertEqual(result['name'], ess_group_args['name'])
        ess_group_args["id"] = result["id"]
        self._ess_configuration["group_id"] = ess_group_args["id"]
        self._ess_configuration["security_group_id"] = self._security_group_args["id"]
        result = run_module(ess_configuration_main, self._ess_configuration)
        ess_group_args["configuration_id"] = result["id"]
        ess_group_args["state"] = "active"
        result = run_module(ess_group_main, ess_group_args)
        self.assertEqual(result['group']["status"], ess_group_args["state"])
        ess_group_args["state"] = "inactive"
        for _ in range(10):
            try:
                result = run_module(ess_group_main, ess_group_args)
            except:
                time.sleep(6)
            else:
                break
        self.assertEqual(result['group']["status"], ess_group_args["state"])
        ess_group_args["state"] = "absent"
        result = run_module(ess_group_main, ess_group_args)
        self.assertNotIn('failed', result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
