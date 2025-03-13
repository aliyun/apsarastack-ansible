# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import uuid
import unittest

from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.plugins.modules.ali_dns_group import main as dns_group_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage


class Test(unittest.TestCase):

    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        load_dotenv()

    def testCreateDnsGroup(self):
        dnsgroup_args = {
            "group_name": "ansible_test_dns_group_%s" % (uuid.uuid1())

        }
        result = run_module(dns_group_main, dnsgroup_args)
        self.assertNotIn('failed', result)
        self.assertEqual(result['changed'], False)
        self.assertEqual(result['group_name'], dnsgroup_args["group_name"])

        dnsgroup_args = {
            "state": "absent",
            "group_id": result["group_id"],
        }
        result = run_module(dns_group_main, dnsgroup_args)
        self.assertNotIn('failed', result, result.get('msg', ''))
        
        

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
