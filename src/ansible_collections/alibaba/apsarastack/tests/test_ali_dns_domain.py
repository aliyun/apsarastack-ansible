# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import uuid
import unittest

from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.plugins.modules.ali_dns_domain import main as dns_domain_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage


class Test(unittest.TestCase):

    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        load_dotenv()

    def testCreateDnsDomain(self):
        dnsdomain_args = {
            "domain_name": "zhangyantest123.dev.ali.cloud.cn.hsbcv6."

        }
        result = run_module(dns_domain_main, dnsdomain_args)
        self.assertNotIn('failed', result)
        self.assertEqual(result['changed'], False)
        self.assertEqual(result["dns"]["Name"], dnsdomain_args["domain_name"])

        dnsdomain_args = {
            "remark": "remark_test",
            "domain_name": "zhangyantest123.dev.ali.cloud.cn.hsbcv6."
        }
        result = run_module(dns_domain_main, dnsdomain_args)
        self.assertNotIn('failed', result)
        self.assertEqual(result['changed'], True)
        self.assertEqual(result["dns"]["Remark"], dnsdomain_args["remark"])

        dnsdomain_args = {
            "state": "absent",
            "domain_name": result["dns"]["Name"],
        }
        result = run_module(dns_domain_main, dnsdomain_args)
        self.assertNotIn('failed', result, result.get('msg', ''))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
