# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import unittest

from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.plugins.modules.ali_dns_domain import main as dns_domain_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_dns_domain_info import main as dns_domain_info_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage


class Test(unittest.TestCase):

    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self.dns_domain_args = {
            "remark": "remark_test",
            "domain_name": "zhangyantest123.dev.ali.cloud.cn.hsbcv6."
        } 
    def setUp(self)->None:
        unittest.TestCase.setUp(self)
        load_dotenv()
        result = run_module(dns_domain_main, self.dns_domain_args)

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        dns_domain_args = {
            "state": "absent",
            "domain_name": self.dns_domain_args['domain_name'],
        }
        run_module(dns_domain_main, dns_domain_args)

    def testDescribediskInfo(self):        
        dns_domain__args = {
            "domain_name": self.dns_domain_args['domain_name'],
        }
        result = run_module(dns_domain_info_main, dns_domain__args)
        self.assertEqual(result["dns"]['Name'], self.dns_domain_args["domain_name"])
        self.assertEqual(result["dns"]['Remark'], self.dns_domain_args["remark"])


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreatedisk']
    run_unittest_with_coverage()
