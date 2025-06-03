# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import unittest
from urllib.parse import unquote
from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_oss_bucket import main as oss_bucket_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_oss_object import main as oss_object_main
class Test(unittest.TestCase):

    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self.bucket_args = {
            "state": "present",
            "permission": "public-read-write",
            "bucket_name": 'test-bucket',
        }
        self.file_name = "ansiable_test_oss_object.txt"
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

    def testCreateBucketObject(self):
        bucket_obj_args = {
            "bucket": self.bucket_args["bucket_name"],
            "mode": "put",
            "permission": 'public-read-write',
            "content": "binary/octet-stream",
            "object": "test-object/",
        }
        result = run_module(oss_object_main, bucket_obj_args)
        self.assertEqual(unquote(result["object"]["Key"]), bucket_obj_args["object"])
        with open(self.file_name, "w") as f:
            f.write("test_oss_object")
        bucket_obj_args["file_name"] = self.file_name
        del bucket_obj_args["content"]
        result = run_module(oss_object_main, bucket_obj_args)
        bucket_obj_args = {
            "bucket": self.bucket_args["bucket_name"],
            "mode": "put",
            "permission": 'private',
            "content": "binary/octet-stream",
            "object": "test-object/%s" % self.file_name,
        }
        result = run_module(oss_object_main, bucket_obj_args)
        self.assertEqual(result["changed"], bucket_obj_args["permission"])
        bucket_obj_args = {
            "bucket": self.bucket_args["bucket_name"],
            "mode": "put",
            "permission": 'public-read-write',
            "content": "binary/octet-stream",
            "object": "test-object/%s" % self.file_name,
        }
        result = run_module(oss_object_main, bucket_obj_args)
        self.assertEqual(result["changed"], bucket_obj_args["permission"])
        bucket_obj_args = {
            "bucket": self.bucket_args["bucket_name"],
            "mode": "delete",
            "permission": 'public-read-write',
            "content": "binary/octet-stream",
            "object": "test-object/%s" % self.file_name,
        }
        result = run_module(oss_object_main, bucket_obj_args)
        self.assertEqual(unquote(result["key"]), bucket_obj_args["object"])
        bucket_obj_args = {
            "bucket": self.bucket_args["bucket_name"],
            "mode": "delete",
            "permission": 'public-read-write',
            "content": "binary/octet-stream",
            "object": "test-object/",
        }
        result = run_module(oss_object_main, bucket_obj_args)
        self.assertEqual(unquote(result["key"]), bucket_obj_args["object"])


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
