# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import unittest

from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_oss_bucket import main as oss_bucket_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_oss_bucket_info import main as oss_bucket_info_main
class Test(unittest.TestCase):

    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self.bucket_args = {
            "state": "present",
            "permission": "private",
            "bucket_name": 'test-bucket',
        }
    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        load_dotenv()
        result = run_module(oss_bucket_main, self.bucket_args)

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        self.bucket_args["state"] = "absent"
        try:
            run_module(oss_bucket_main, self.bucket_args)
        except:
            pass

    def testdescribebucket(self):
        bucket_describe_param = {
            "bucket_prefix": "test-"
        }
        result = run_module(oss_bucket_info_main, bucket_describe_param)
        self.assertIn(self.bucket_args["bucket_name"], result["bucket_names"])
        self.assertIn(self.bucket_args["bucket_name"], [x["Name"] for x in result["buckets"]])
        


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
