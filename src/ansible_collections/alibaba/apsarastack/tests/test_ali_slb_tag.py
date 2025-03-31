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
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_slb_lb import main as slb_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_slb_tag import main as slb_tag_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage

class Test(unittest.TestCase):

    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self.name = "ansible_test_slb_tag_%s" % uuid.uuid1()
        self.tag_key = "ansible_test_slb_tag"
        self.tag_value = "ansible"
        self._vpc_args = {
            "cidr_block": "172.16.0.0/16",
            "vpc_name": self.name,
            "description": "create by ansible unit test",
        }
        self._vswtich_args = {
            "cidr_block": "172.16.1.0/24",
            "name": self.name
        }
        self._slb_args = {
            "internet_charge_type": "PayByTraffic",
            "load_balancer_name": self.name,
            "load_balancer_spec": "slb.s1.small",
            "purge_tags": False,
        }

    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        load_dotenv()
        result = run_module(vpc_main, self._vpc_args)
        self._vpc_args['id'] = result['vpc']['vpc_id']
        self._vswtich_args["vpc_id"] = result['vpc']['vpc_id']
        result = run_module(vswtich_main, self._vswtich_args)
        self._vswtich_args["id"] = result['vswitch']['vswitch_id']
        self._slb_args["vswitch_id"] = result['vswitch']['vswitch_id']
        result = run_module(slb_main, self._slb_args)
        self._slb_args["id"] = result['load_balancer']['load_balancer_id']


    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        vswitch = {
            "state": "absent",
        } | self._vswtich_args
        vpc_args = {
            "state": "absent",
        } | self._vpc_args
        slb_args = {
            "state": "absent",
        } | self._slb_args
        try:
            run_module(vswtich_main, vswitch)
            run_module(vpc_main, vpc_args)
            run_module(slb_main, slb_args)
        except:
            pass


    def testSlbTag(self):
        tags_args = {
            "resource_id": self._slb_args['id'],
            "tags": {
                "aaa": "bbb"
            }
        }
        result = run_module(slb_tag_main, tags_args)
        self.assertNotIn('failed', result)
        tags = result["tags"]
        self.assertEqual(tags["aaa"], "bbb")
        self.assertEqual(len(tags), 1)
        tags_args["tags"] = {
            "bbbb": "22222222",
            "cccc": "3333333"
        }
        result = run_module(slb_tag_main, tags_args)
        self.assertNotIn('failed', result)
        tags = result["tags"]
        self.assertEqual(tags["bbbb"], "22222222")
        self.assertEqual(tags["cccc"], "3333333")
        self.assertEqual(len(tags), 2)
        
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
