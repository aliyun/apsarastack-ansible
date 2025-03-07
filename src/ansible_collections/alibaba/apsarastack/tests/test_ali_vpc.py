# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import unittest

from ansible_collections.alibaba.apsarastack.plugins.modules.ali_vpc import main as vpc_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module
from dotenv import load_dotenv


class Test(unittest.TestCase):

    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        load_dotenv()

    def testCreateVpc(self):
        vpc_args = {
            "state": "present",
            "cidr_block": "192.168.0.0/24",
            "vpc_name": "ansible_test_vpc",
            "description": "create by ansible unit test",
        }

        result = run_module(vpc_main, vpc_args)
        self.assertNotIn('failed', result, result.get('msg', ''))

        vpc_args = {
            "state": "absent",
            "cidr_block": "192.168.0.0/24",
            "vpc_id": result['vpc']['vpc_id'],
        }
        result = run_module(vpc_main, vpc_args)
        self.assertNotIn('failed', result, result.get('msg', ''))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    unittest.main()
