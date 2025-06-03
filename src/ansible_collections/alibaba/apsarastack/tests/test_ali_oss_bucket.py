# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import unittest

from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_oss_bucket import main as oss_bucket_main

class Test(unittest.TestCase):

    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        load_dotenv()

    def testCreateBucket(self):
        bucket_args = {
            "state": "present",
            "permission": "private",
            "bucket_name": 'test-bucket',
        }
        result = run_module(oss_bucket_main, bucket_args)
        self.assertEqual(result['bucket']["Name"], bucket_args["bucket_name"])
        bucket_args = {
            "state": "absent",
            "permission": "private",
            "bucket_name": 'test-bucket',
        }
        result = run_module(oss_bucket_main, bucket_args)
        self.assertNotIn('failed', result)
        self.assertTrue(result["changed"])


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
