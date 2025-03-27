# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''

import unittest

from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.plugins.modules.ali_eip import main as eip_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage

class Test(unittest.TestCase):

    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        load_dotenv()

    def testCreateEip(self):
        eip_args = {
            "name": "test_ansible_eip",
            "description": "This is a test EIP address for ansible.",
            "bandwidth": "5",
            "isp": "CMCC_AZ1",
            "netmode": "hybrid"
        }
        result = run_module(eip_main, eip_args)
        self.assertNotIn('failed', result)
        self.assertIsNotNone(result['eip'])
        eip = result["eip"]
        self.assertEqual(eip['name'], eip_args['name'])
        self.assertEqual(eip['description'], eip_args['description'])
        self.assertEqual(eip['bandwidth'], eip_args['bandwidth'])
        self.assertEqual(result["invocation"]["module_args"]["isp"], eip_args['isp'])
        self.assertEqual(eip['netmode'], eip_args['netmode'])
        eip1_args = {
            "name": "test_ansible_eip1",
            "description": "This is a test EIP1 address for ansible.",
            "bandwidth": "10",
        }
        result = run_module(eip_main, eip1_args)
        self.assertNotIn('failed', result)
        self.assertIsNotNone(result['eip'])
        eip1 = result["eip"]
        self.assertEqual(eip1['id'], eip['id'])
        self.assertEqual(eip1['name'], eip1_args['name'])
        self.assertEqual(eip1['description'], eip1_args['description'])
        self.assertEqual(eip1['bandwidth'], eip1_args['bandwidth'])

        


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
