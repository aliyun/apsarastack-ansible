# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import unittest
import uuid

from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vpc import main as vpc_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vswitch import main as vswtich_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_rds_database_info import main as rds_database_info_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_rds_instance import main as rds_instance_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_rds_database import main as rds_database_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage


class Test(unittest.TestCase):

    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self.name = "ansible_test_rds_database_info_%s" % uuid.uuid1()
        self.dbname = "ansible_test_rds_database_info"
        self._vpc_args = {
            "cidr_block": "172.16.0.0/16",
            "vpc_name": self.name,
            "description": "create by ansible unit test",
        }
        self._vswtich_args = {
            "cidr_block": "172.16.1.0/24",
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
        
        self._rds_database = {
        "db_name": self.dbname,
        "character_set_name": "utf8",
        "db_description": "ansible_test"
                }

    def setUp(self)->None:
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
        self._rds_database["instance_id"] = result['instances']['id']
        result = run_module(rds_database_main, self._rds_database)

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        rds_database = {
            "state": "absent",
        } | self._rds_database
        run_module(rds_database_main, rds_database)
        rds_instance_args = {
            "state": "absent",
            "db_instance_id": self._rds_instance_args["id"]
        }
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

    def testDescribeRdsDatabaseInfo(self):        
        rds_account_info_args = {
            "name_prefix": 'ansible_test_rds_database',
            "db_instance_id": self._rds_instance_args["id"]
        }
        result = run_module(rds_database_info_main, rds_account_info_args)
        self.assertIn(self.dbname, [x["name"] for x in result["databases"]])

        rds_account_info_args = {
            "status": 'Running',
            "db_instance_id": self._rds_instance_args["id"]
        }
        result = run_module(rds_database_info_main, rds_account_info_args)
        self.assertIn(self.dbname, [x["name"] for x in result["databases"]])


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreatedisk']
    run_unittest_with_coverage()
