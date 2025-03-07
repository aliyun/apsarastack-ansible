# encoding: utf-8
'''
Created on 2025年3月7日

@author: jingyu.wy
'''
import io
import json
from unittest import mock
from ansible.module_utils import basic as module_utils_basic


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
