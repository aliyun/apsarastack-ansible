# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import unittest
import uuid

from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.plugins.modules.ali_slb_lb import main as slb_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vpc import main as vpc_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vswitch import main as vswtich_main

class Test(unittest.TestCase):

    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self.name = "ansible_test_slb_%s" % uuid.uuid1()
        self._vpc_args = {
            "cidr_block": "172.16.0.0/16",
            "vpc_name": self.name,
            "description": "create by ansible unit test",
        }
        self._vswtich_args = {
            "cidr_block": "172.16.1.0/24",
            "name": self.name
        }

    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        load_dotenv()
        result = run_module(vpc_main, self._vpc_args)
        self._vpc_args['id'] = result['vpc']['vpc_id']
        self._vswtich_args["vpc_id"] = result['vpc']['vpc_id']
        result = run_module(vswtich_main, self._vswtich_args)
        self._vswtich_args["id"] = result['vswitch']['vswitch_id']

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        vswitch = {
            "state": "absent",
        } | self._vswtich_args
        vpc_args = {
            "state": "absent",
        } | self._vpc_args
        try:
            run_module(vswtich_main, vswitch)
            run_module(vpc_main, vpc_args)
        except:
            pass

    def testCreateSlb(self):
        slb_args = {
            "internet_charge_type": "PayByTraffic",
            "load_balancer_name": self.name,
            "load_balancer_spec": "slb.s1.small",
            "tags": {"ansible_test_tag": "ansible"},
            "purge_tags": True,
            "vswitch_id": self._vswtich_args["id"]

        }
        result = run_module(slb_main, slb_args)
        import pdb;pdb.set_trace()
        self.assertNotIn('failed', result)
        self.assertEqual(result['changed'], False)
        self.assertEqual(result['vpc'], {})
        
        vpc_args = {
            "state": "present",
            "cidr_block": "192.168.0.0/24",
            "vpc_name": "ansible_test_vpc",
            "description": "create by ansible unit test",
        }
        result = run_module(vpc_main, vpc_args)
        self.assertNotIn('failed', result, result.get('msg', ''))
        self.assertEqual(result['vpc']['vpc_name'], vpc_args['vpc_name'])
        
        vpc_args = {
            "state": "present",
            "cidr_block": "192.168.0.0/24",
            "vpc_name": "ansible_test_vpc",
            "description": "modify by ansible unit test",
        }
        result = run_module(vpc_main, vpc_args)
        self.assertNotIn('failed', result, result.get('msg', ''))
        self.assertTrue(result['changed'])
        self.assertEqual(result['vpc']['description'], vpc_args['description'])
        
        vpc_args = {
            "state": "present",
            "cidr_block": "192.168.0.0/24",
            "vpc_name": "ansible_test_vpc",
            "description": "modify by ansible unit test",
            "tags": {"key1":"value1"}
        }
        result = run_module(vpc_main, vpc_args)
        self.assertNotIn('failed', result, result.get('msg', ''))
        self.assertTrue(result['changed'])
        # TODO: 无法读取到tag信息
        
        vpc_args = {
            "state": "present",
            "cidr_block": "192.168.0.0/24",
            "vpc_name": "ansible_test_vpc",
            "description": "modify by ansible unit test",
            "purge_tags": True
        }
        result = run_module(vpc_main, vpc_args)
        self.assertNotIn('failed', result, result.get('msg', ''))
        self.assertTrue(result['changed'])

        vpc_args = {
            "state": "absent",
            "cidr_block": "192.168.0.0/24",
            "vpc_id": result['vpc']['vpc_id'],
        }
        result = run_module(vpc_main, vpc_args)
        self.assertNotIn('failed', result, result.get('msg', ''))

        vpc_args = {
            "cidr_block": "192.168.0.0/24",
            "vpc_name": "http://ansible_test_vpc",
            "description": "modify by ansible unit test",
        }
        result = run_module(vpc_main, vpc_args)
        self.assertIn('failed', result)
        self.assertEqual(result['msg'], 'vpc_name can not start with http:// or https://')
        
        vpc_args = {
            "cidr_block": "192.168.0.0/24",
            "vpc_name": "ansible_test_vpc",
            "description": "http://modify by ansible unit test",
        }
        result = run_module(vpc_main, vpc_args)
        self.assertIn('failed', result)
        self.assertEqual(result['msg'], 'description can not start with http:// or https://')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
