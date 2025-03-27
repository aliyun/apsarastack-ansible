# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''

import unittest

from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.plugins.modules.ali_eip import main as eip_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_eip_info import main as eip_info_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage


class Test(unittest.TestCase):

    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self._eip_info = {
            "name": "test_ansible_eip",
            "description": "This is a test EIP address for ansible.",
            "bandwidth": "5",
        }

    def setUp(self)->None:
        unittest.TestCase.setUp(self)
        load_dotenv()
        eip_args = self._eip_info
        result = run_module(eip_main, eip_args)
        self._eip_info['id'] = result['eip']['id']

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        eip_args = {
            "status": "available",
        } | self._eip_info
        run_module(eip_main, eip_args)

    def testDescribeEipInfo(self):        
        eip_info_args = {
            "name_prefix": 'test_ansible',
        }
        result = run_module(eip_info_main, eip_info_args)
        print(result)
        self.assertEqual(len(result['eips']), 1,)
        self.assertEqual(result['eips'][0]['id'], self._eip_info['id'])
        eip_info_args = {
            "name_prefix": '_test_ansible',
        }
        result = run_module(eip_info_main, eip_info_args)
        self.assertEqual(len(result['eips']), 0,)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreatedisk']
    run_unittest_with_coverage()
