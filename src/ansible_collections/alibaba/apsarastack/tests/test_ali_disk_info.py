# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import unittest
import uuid

from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.plugins.modules.ali_disk import main as disk_main
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_disk_info import main as disk_info_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage


class Test(unittest.TestCase):

    def __init__(self, methodName:str="runTest") -> None:
        unittest.TestCase.__init__(self, methodName=methodName)
        self._disk_info = {
            "disk_category": "cloud_ssd",
            "size": "30",
            "disk_name": "New-diskv%s" % uuid.uuid1(),
            "description": "new_disk",
            "tags": [{"key1": "values1"}]
        }

    def setUp(self)->None:
        unittest.TestCase.setUp(self)
        load_dotenv()
        disk_args = self._disk_info
        result = run_module(disk_main, disk_args)
        print(result)
        self._disk_info['id'] = result['disk']['id']

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        disk_args = {
            "state": "absent",
        } | self._disk_info
        run_module(disk_main, disk_args)

    def testDescribediskInfo(self):        
        disk_info_args = {
            "name_prefix": 'New-diskv',
        }
        result = run_module(disk_info_main, disk_info_args)
        self.assertEqual(len(result['disks']), 1,)
        self.assertEqual(result['disks'][0]['id'], self._disk_info['id'])
        disk_info_args = {
            "name_prefix": '_New-diskv',
        }
        result = run_module(disk_info_main, disk_info_args)
        self.assertEqual(len(result['disks']), 0,)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreatedisk']
    run_unittest_with_coverage()
