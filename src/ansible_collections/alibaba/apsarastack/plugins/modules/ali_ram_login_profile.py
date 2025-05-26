#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017-present Alibaba Group Holding Limited. He Guimin <heguimin36@163.com.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible. If not, see http://www.gnu.org/licenses/.

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = """
---
module: ali_ram_login_profile
short_description: Create, Delete, Update Ram login profile in Alibaba Cloud.
description:
    - Create, Delete, Update Ram login profile in Alibaba Cloud.
options:
  state:
    description:
      - If I(state=present), ram login profile will be created.
      - If I(state=present) and login profile exists, it will be updated.
      - If I(state=absent), ram login profile will be removed.
    default: 'present'
    choices: ['present', 'absent']
    type: str
  user_name:
    description:
      - The username.
    aliases: ['name']
    required: True
    type: str
  password:
    description:
      - The password.
    type: str 
  new_password:
    description:
      - The new password. Required when update password.
    type: str
  password_reset_required:
    description:
      - Specifies whether you need to change your password upon logon.
    default: False
    type: bool
  mfa_bind_required:
    description:
      - Specifies whether you need to attach an MFA device upon the next logon.
    default: False
    type: bool
requirements:
    - "python >= 3.6"
    - "footmark >= 1.17.0"
extends_documentation_fragment:
    - apsarastack
author:
  - "He Guimin (@xiaozhu36)"
"""

EXAMPLES = """
# Note: These examples do not set authentication details, see the Alibaba Cloud Guide for details.
- name: Changed. Create login profile
  ali_ram_login_profile:
    user_name: ansible
    password: YourPassword
    password_reset_required: True

- name: Changed. update login profile
  ali_ram_login_profile:
    user_name: ansible
    password: YourNewPassword

- name: Changed. Delete login profile
  ali_ram_login_profile:
    state: absent
    user_name: ansible
"""

RETURN = '''
user:
    description: Returns an array of complex objects as described below.
    returned: always
    type: complex
    contains:
        create_date:
            description: The creation time.
            returned: always
            type: str
            sample: '2015-01-23T12:33:18Z'
        mfabind_required:
            description: Indicates that you must attach an MFA device.
            returned: always
            type: bool
            sample: False
        password_reset_required:
            description: Indicates that you must change your password upon next logon.
            returned: always
            type: bool
            sample: False
        user_name:
            description: The username.
            returned: always
            type: str
            sample: Alice
'''
import json
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.alibaba.apsarastack.plugins.module_utils.apsarastack_common import common_argument_spec
from ansible_collections.alibaba.apsarastack.plugins.module_utils.apsarastack_connections import ram_connect, do_common_request

HAS_FOOTMARK = False

try:
    from footmark.exception import RAMResponseError
    HAS_FOOTMARK = True
except ImportError:
    HAS_FOOTMARK = False


def profile_exists(module, ram_conn, name, profile_id=None):
    if profile_id:
        return True
    params = {
        "name": name
    }
    try:
        response = do_common_request(
            ram_conn, "POST", "ascm", "2019-05-10", "ListLoginPolicies", "/ascm/auth/loginPolicy/listLoginPolicies", body=params)
        for policy in response["data"]:
            if policy["name"] == name:
                return policy
    except Exception as e:
        return module.fail_json(msg="Failed to describe policy: {0}".format(e))
    

def create_profile(module, ram_conn):
    params = {
        "organizationVisibility": "organizationVisibility." + module.params['organization_visibility'],
        "rule" : module.params['rule'],
        "name": module.params['name'],
        "description": module.params['description']
    }
    try:
        do_common_request(
            ram_conn, "POST", "ascm", "2019-05-10", "AddLoginPolicy", "/ascm/auth/loginPolicy/addLoginPolicy", body=params)
        return profile_exists(module, ram_conn, module.params['name'])
    except Exception as e:
        return module.fail_json(msg="Failed to create policy: {0}".format(e))
    

def update_profile(module, ram_conn):
    try:
        do_common_request(
            ram_conn, "POST", "ascm", "2019-05-10", "ModifyLoginPolicy", "/ascm/auth/loginPolicy/modifyLoginPolicy", body=module.params)
        return profile_exists(module, ram_conn, module.params['name'])
    except Exception as e:
        return module.fail_json(msg="Failed to modify policy: {0}".format(e))
    
def delete_profile(module, ram_conn, name):
    params = {
        "name": name
    }
    try:
        do_common_request(
            ram_conn, "POST", "ascm", "2019-05-10", "RemoveLoginPolicyByName", "/ascm/auth/loginPolicy/removeLoginPolicyByName", body=params)
        return profile_exists(module, ram_conn, module.params['name'])
    except Exception as e:
        return module.fail_json(msg="Failed to delete policy: {0}".format(e))

def main():
    argument_spec = common_argument_spec()
    argument_spec.update(dict(
        state=dict(default='present', choices=['present', 'absent']),
        name=dict(type='str', required=True, aliases=['user_name']),
        organization_visibility=dict(type='str'),
        description=dict(type='str'),
        rule=dict(type='str'),
        id=dict(type='str'),
    ))

    module = AnsibleModule(argument_spec=argument_spec)

    if HAS_FOOTMARK is False:
        module.fail_json(msg='footmark required for this module.')

    ram_conn = ram_connect(module)

    # Get values of variable
    state = module.params['state']
    user_name = module.params['name']
    changed = False
    id = module.params['id']

    # Check if profile exists
    profile = profile_exists(module, ram_conn, user_name, profile_id=id)
    # module.exit_json(changed=True, profile=profile.read())

    if state == 'absent':
        if not profile:
            module.exit_json(changed=changed, profile={})
        try:
            changed = delete_profile(module, ram_conn, user_name)
            module.exit_json(changed=changed, profile={})
        except RAMResponseError as ex:
            module.fail_json(msg='Unable to delete profile error: {}'.format(ex))

    if not profile:
        try:
            profile = create_profile(module, ram_conn)
            module.exit_json(changed=True, profile=profile)
        except RAMResponseError as e:
            module.fail_json(msg='Unable to create profile, error: {0}'.format(e))

    try:
        profile = update_profile(module, ram_conn)
        module.exit_json(changed=True, profile=profile)
    except Exception as e:
        module.fail_json(msg='Unable to update profile, error: {0}'.format(e))


if __name__ == '__main__':
    main()

