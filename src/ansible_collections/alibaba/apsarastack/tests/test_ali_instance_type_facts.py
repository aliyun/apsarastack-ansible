# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import os
import unittest


from dotenv import load_dotenv

from ansible_collections.alibaba.apsarastack.plugins.modules.ali_instance_type_facts import main as instance_type_facts_main
from ansible_collections.alibaba.apsarastack.tests.test_utils import run_module, run_unittest_with_coverage


class Test(unittest.TestCase):

    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        load_dotenv()

    def testDescribeInstanceType(self):
        instance_type_args = {
        }
        result = run_module(instance_type_facts_main, instance_type_args)
        self.assertNotIn('failed', result)
        instance_type_id = result["instance_type_ids"][0]
        cpu_count = result["instance_types"][0]["cpu_core_count"]
        memory_size = result["instance_types"][0]["memory_size"]
        instance_type_args = {
            "instance_type_ids": [instance_type_id]
        }
        result = run_module(instance_type_facts_main, instance_type_args)
        self.assertEqual(len(result["instance_type_ids"]), 1)
        self.assertEqual(result["instance_type_ids"][0], instance_type_id)

        instance_type_args = {
            "cpu_core_count": cpu_count
        }
        result = run_module(instance_type_facts_main, instance_type_args)
        self.assertEqual(len({x["cpu_core_count"] for x in result["instance_types"]}), 1)
        self.assertEqual({x["cpu_core_count"] for x in result["instance_types"]}, {cpu_count})

        instance_type_args = {
            "memory_size": memory_size
        }
        result = run_module(instance_type_facts_main, instance_type_args)
        self.assertEqual(len({x["memory_size"] for x in result["instance_types"]}), 1)
        self.assertEqual({x["memory_size"] for x in result["instance_types"]}, {memory_size})

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateVpc']
    run_unittest_with_coverage()
