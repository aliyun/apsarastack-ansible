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
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_oss_object import main as oss_object_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_oss_object_info import main as oss_object_info_main
class Test(unittest.TestCase):

    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self.bucket_args = {
            "state": "present",
            "permission": "public-read-write",
            "bucket_name": 'test-bucket',
        }
        self.bucket_obj_args = {
            "bucket": self.bucket_args["bucket_name"],
            "mode": "put",
            "permission": 'public-read-write',
            "content": "binary/octet-stream",
            "object": "test-object",
        }
        self.bucket_obj_args_v2 = {
            "bucket": self.bucket_args["bucket_name"],
            "mode": "put",
            "permission": 'public-read-write',
            "content": "binary/octet-stream",
            "object": "test-object-v2",
        }
    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        load_dotenv()
        run_module(oss_bucket_main, self.bucket_args)
        run_module(oss_object_main, self.bucket_obj_args)
        run_module(oss_object_main, self.bucket_obj_args_v2)

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        self.bucket_args["state"] = "absent"
        self.bucket_obj_args["mode"] = "delete"
        self.bucket_obj_args_v2["mode"] = "delete"
        try:
            run_module(oss_object_main, self.bucket_obj_args)
            run_module(oss_object_main, self.bucket_obj_args_v2)
            run_module(oss_bucket_main, self.bucket_args)
        except:
            pass

    def testdescribebucketObject(self):
        object_describe_param = {
            "object": "test-",
            "bucket": self.bucket_args["bucket_name"]
        }
        result = run_module(oss_object_info_main, object_describe_param)
        contents = result["objects"]["Data"]["ListBucketResult"]["Contents"]
        keys = [x["Key"] for x in contents]
        self.assertIn(self.bucket_obj_args_v2["object"], keys)
        self.assertIn(self.bucket_obj_args["object"], keys)
        


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
