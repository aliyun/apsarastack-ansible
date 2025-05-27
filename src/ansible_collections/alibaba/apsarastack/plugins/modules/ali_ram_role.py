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
module: ali_ram_role
short_description: Create, Delete, Update Ram Role in Alibaba Cloud.
description:
    - Create, Delete, Update Role in Alibaba Cloud.
    - An unique ali_ram_role module is determined by parameters role_name. 
options:        
  state:
    description:
      - If I(state=present), role will be created.
      - If I(state=present), and assume_role_policy_document exists, role will be updated.
      - If I(state=absent), role will be removed.
    choices: ['present', 'absent']
    default: 'present'
    type: str
  role_name:
    description:
      - The name of the RAM role. The specified name can be up to 64 characters in length. Format(^[a-zA-Z0-9\. @\-]+$)
      - One of I(role_name) and I(role_id) must be specified when operate existing role.
    aliases: ['name']
    type: str
  role_id:
    description:
      - The id of the RAM role.
      - One of I(role_name) and I(role_id) must be specified when operate existing role.
    aliases: ['id']
    type: str
  assume_role_policy_document:
    description:
      - The policy text that specifies one or more entities entrusted to assume the RAM role. 
        The trusted entity can be an Alibaba Cloud account, Alibaba Cloud service, or identity provider (IdP).
      - Required when C(state=present)
    type: str
    aliases: ['policy']
  description:
    description:
      - The description of the RAM role. The description can be up to 1,024 characters in length.
    type: str
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
- name: Changed. Create a role
  ali_ram_role:
    role_name: ansible
    policy: '{"Statement": [{"Action": "sts:AssumeRole","Effect": "Allow","Principal": {"Service": ["rds.aliyuncs.com"]}}],"Version": "1"}'
    description: create for ansible

- name: Changed. Update role
  ali_ram_role:
    role_name: ansible
    policy: '{"Statement": [{"Action": "sts:AssumeRole","Effect": "Allow","Principal": {"Service": ["ecs.aliyuncs.com"]}}],"Version": "1"}'

- name: Changed. Delete role
  ali_ram_role:
    state: absent
    role_name: ansible
"""

RETURN = '''
user:
    description: Returns an array of complex objects as described below.
    returned: always
    type: complex
    contains:
        arn:
            description: The Alibaba Cloud Resource Name (ARN) of the RAM role.
            returned: always
            type: str
            sample: acs:ram::123456789012****:role/ECSAdmin
        assume_role_policy_document:
            description: The policy text that specifies one or more entities entrusted to assume the RAM role.
            returned: always
            type: str
            sample: '{ "Statement": [ { "Action": "sts:AssumeRole", "Effect": "Allow", "Principal": { "RAM": "acs:ram::123456789012****:root" } } ], "Version": "1" }'
        create_date:
            description: The date and time when the RAM role was created.
            returned: always
            type: str
            sample: '2015-01-23T12:33:18Z'
        description:
            description: The description of the RAM role.
            returned: always
            type: str
            sample: ECS administrator
        role_id:
            description: The ID of the RAM role.
            returned: always
            type: str
            sample: 901234567890****
        role_name:
            description: The name of the RAM role.
            returned: always
            type: str
            sample: ECSAdmin
'''
import json
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.alibaba.apsarastack.plugins.module_utils.apsarastack_connections import ram_connect, do_common_request
from ansible_collections.alibaba.apsarastack.plugins.module_utils.apsarastack_common import common_argument_spec

HAS_FOOTMARK = False

try:
    from footmark.exception import RAMResponseError
    HAS_FOOTMARK = True
except ImportError:
    HAS_FOOTMARK = False


def role_exists(module, ram_conn, role_name, role_id=None):
    if role_id:
        return True
    params = {
        "roleName": role_name
        # "roleType" : "ROLETYPE_ASCM"
    }
    try:
        response = do_common_request(
            ram_conn, "POST", "ascm", "2019-05-10", "ListRoles", "/ascm/auth/role/listRoles", body=params)
        for role in response["data"]:
            if role["roleName"] == role_name:
                return role
    except Exception as e:

        return module.fail_json(msg="Failed to describe Roles: {0}".format(e))
    
def create_role(module, ram_conn):
    params = {
        "organizationVisibility": "organizationVisibility.global",
        "roleRange": "roleRange.%s" % module.params['role_range'],
        "roleName": module.params['role_name'],
        "description": module.params['description'],
    }
    if module.params.get("assumerole_policydocument"):
        params["assumeRolePolicyDocument"] = json.dumps(module.params.get("assumerole_policydocument"))
    try:
        do_common_request(ram_conn, "POST", "ascm", "2019-05-10", "CreateRole", "/ascm/auth/role/createRole", body=params)
        return role_exists(module, ram_conn, module.params['role_name'])
    except Exception as e:

        return module.fail_json(msg="Failed to create Roles: {0}".format(e))
    

def delete_role(module, ram_conn, role_name):
    params = {
        "roleName": role_name
    }
    try:
        do_common_request(ram_conn, "POST", "ascm", "2019-05-10", "RemoveRole", "/ascm/auth/role/removeRole", body=params)
        return role_exists(module, ram_conn, role_name)
    except Exception as e:

        return module.fail_json(msg="Failed to create Roles: {0}".format(e))
    
def modify_role(module, ram_conn):
    params = {
        "roleId": module.params['role_id']
    }
    if module.params.get("role_name"):
        params["newRoleName"] = module.params['role_name']
    if module.params.get("role_range"):
        params["newRoleRange"] = "roleRange.%s" % module.params['role_range']
    if module.params.get("description"):
        params["newDescription"] = module.params['description']
    try:
        do_common_request(ram_conn, "POST", "ascm", "2019-05-10", "UpdateRoleInfo", "/ascm/auth/role/updateRoleInfo", body=params)
        return role_exists(module, ram_conn, module.params['role_name'])
    except Exception as e:

        return module.fail_json(msg="Failed to create Roles: {0}".format(e))
    

def main():
    argument_spec = common_argument_spec()
    argument_spec.update(dict(
        state=dict(default='present', choices=['present', 'absent']),
        role_name=dict(type='str', aliases=['name']),
        role_id=dict(type='str', aliases=['id']),
        assume_role_policy_document=dict(type='str', aliases=['policy']),
        description=dict(type='str'),
        role_range=dict(type='str'),
        assumerole_policydocument=dict(type='dict'),
    ))

    module = AnsibleModule(argument_spec=argument_spec)

    if HAS_FOOTMARK is False:
        module.fail_json(msg='footmark required for this module.')

    ram_conn = ram_connect(module)

    # Get values of variable
    state = module.params['state']
    role_name = module.params['role_name']
    assume_role_policy_document = module.params['assume_role_policy_document']
    role_id = module.params['role_id']
    changed = False

    # Check if role exists
    role = role_exists(module, ram_conn, role_name, role_id)

    if state == 'absent':
        if not role:
            module.exit_json(changed=changed, role={})
        try:
            module.exit_json(changed=delete_role(module, ram_conn, role_name), role={})
        except RAMResponseError as ex:
            module.fail_json(msg='Unable to delete role {0}, error: {1}'.format(role_name, ex))

    if not role:
        try:
            role = create_role(module, ram_conn)
            module.exit_json(changed=True, role=role)
        except RAMResponseError as e:
            module.fail_json(msg='Unable to create role, error: {0}'.format(e))
    else:
        role = modify_role(module, ram_conn)
        if not assume_role_policy_document:
          module.exit_json(changed=True, role=role)

    if assume_role_policy_document:
        try:
            changed = role.update_policy(policy=assume_role_policy_document)
            module.exit_json(changed=changed, role=role.get().read())
        except RAMResponseError as e:
            module.fail_json(msg='Unable to update role policy, error: {0}'.format(e))


if __name__ == '__main__':
    main()
