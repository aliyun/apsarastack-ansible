# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import io
import json
import os
from pathlib import Path
import traceback
from unittest import mock, main

from ansible.module_utils import basic as module_utils_basic

try:
    import coverage

    def run_unittest_with_coverage():
        project = str(Path(__file__).parent.parent.resolve())
        cov = coverage.Coverage(
            source=[project],  # 指定统计的代码目录
        )
        cov.start()
        
        try:
            main()
        except SystemExit:
            pass
        finally:
            cov.stop()
            cov.save()
            
        # 生成报告
        if not os.path.exists('htmlcov'):
            os.mkdir('htmlcov')
        cov.html_report(directory='htmlcov')

except ImportError:

    def run_unittest_with_coverage(func):
        func()


def run_module(module_main_fuc:callable, modules_args:dict) -> dict:
    """执行模块并捕获输出的通用方法"""

    modules_args = {'ANSIBLE_MODULE_ARGS': modules_args}
    stdin = io.BytesIO(json.dumps(modules_args).encode("utf-8"))
    stdin.buffer = stdin
    stdout = io.StringIO()
    
    with mock.patch.multiple("sys", **{"stdin":stdin, "stdout":stdout, "argv":[]}):
        try:
            module_utils_basic._ANSIBLE_ARGS = None
            module_main_fuc()
        except SystemExit:
            pass
        return json.loads(stdout.getvalue())


