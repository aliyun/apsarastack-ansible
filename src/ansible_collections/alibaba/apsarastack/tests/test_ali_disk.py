# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import unittest

from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.plugins.modules.ali_disk import main as disk_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage


class Test(unittest.TestCase):

    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        load_dotenv()

    def testCreateDisk(self):
        disk_args = {
            "disk_category": "cloud_ssd",
            "size": "30",
            "disk_name": "New-diskv2",
            "description": "new_disk",
        }
        result = run_module(disk_main, disk_args)
        self.assertNotIn('failed', result, result.get('msg', ''))
        disk_id = result["disk"]["id"]

        disk_args = {
            "disk_name": "New-diskv3",
            "disk_id": disk_id
        }   
        result = run_module(disk_main, disk_args)
        self.assertNotIn('failed', result, result.get('msg', ''))

        disk_args = {
            "state": "absent",
            "disk_id": disk_id,
        }
        result = run_module(disk_main, disk_args)
        self.assertNotIn('failed', result, result.get('msg', ''))

        disk_args = {
            "disk_name": "New-diskv4",
            "state": "absent"
        }
        result = run_module(disk_main, disk_args)
        print(result)
        self.assertEqual(result.get('msg'), 'Please use disk_id or disk_name to specify one disk for detaching or deleting.')

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
