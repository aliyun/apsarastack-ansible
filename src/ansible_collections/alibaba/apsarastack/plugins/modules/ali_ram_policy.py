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
module: ali_ram_policy
short_description: Create, Delete, Attach and Detach policy in Alibaba Cloud.
description:
    - Create, Delete, Attach and Detach policy in Alibaba Cloud.
    - An unique ali_ram_policy module is determined by parameters policy_name. 
options:
  state:
    description:
      - If I(state=present), policy will be created.
      - If I(state=present), policy and user_name exists, will attach policy to user.
      - If I(state=present), policy and group_name exists, will attach policy to group.
      - If I(state=present), policy and role_name exists, will attach policy to role.      
      - If I(state=absent), policy will be removed.
      - If I(state=absent), and user_name exists, will detach policy from user.
      - If I(state=absent), and group_name exists, will detach policy from group.
      - If I(state=absent), and role_name exists, will detach policy from role.
    choices: ['present', 'absent']
    default: 'present'
    type: str
  policy_document:
    description:
      - The policy text. It can be up to 2048 bytes.
    aliases: ['policy']
    type: str
  policy_name:
    description:
      - The policy name. It must be 1 to 128 characters in length.
      - This is used to determine if the policy already exists.
    aliases: ['name']
    required: True
    type: str
  description:
    description:
      - The policy description. It must be 1 to 1,024 characters in length.
    type: str
  user_name:
    description:
      - The username of the RAM user to which the policy is attached or detached.
    type: str
  group_name:
    description:
      - The groupname of the RAM group to which the policy is attached or detached.
    type: str
  role_name:
    description:
      - The rolename of the RAM role to which the policy is attached or detached.
    type: str
  policy_type:
    description:
      - The policy type. If this parameter is left unspecified, all polices are listed.
    choices: ['System', 'Custom']
    type: str
    aliases: ['type']
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
- name: Changed. Create policy
  ali_ram_policy:
    policy_name: ansible_oss
    policy_document: '{"Statement":[{"Action":["oss:*"],"Effect":"Allow","Resource":["acs:oss:*:*:*"]}],"Version":"1"}'
    description: create for ansible

- name: Changed. Attach policy to user
  ali_ram_policy:
    user_name: ansible
    policy_name: ansible_oss
    policy_type: Custom

- name: Changed. Detach policy from user
  ali_ram_policy:
    state: absent
    user_name: ansible
    policy_name: ansible_oss
    policy_type: Custom

- name: Changed. Attach policy to group
  ali_ram_policy:
    group_name: ansible
    policy_name: ansible_oss
    policy_type: Custom

- name: Changed. Detach policy from group
  ali_ram_policy:
    state: absent
    group_name: ansible
    policy_name: ansible_oss
    policy_type: Custom

- name: Changed. Attach policy to role
  ali_ram_policy:
    role_name: ansible
    policy_name: ansible_oss
    policy_type: Custom

- name: Changed. Detach policy from role
  ali_ram_policy:
    state: absent
    role_name: ansible
    policy_name: ansible_oss
    policy_type: Custom

- name: Changed. Delete policy
  ali_ram_policy:
    state: absent
    policy_name: ansible_oss
"""

RETURN = '''
policy:
    description: Returns an array of complex objects as described below.
    returned: always
    type: complex
    contains:
        attachment_count:
            description: The number of times that the policy is referenced.
            returned: always
            type: int
            sample: 0
        create_date:
            description: The date and time when the policy was created.
            returned: always
            type: str
            sample: '2015-01-23T12:33:18Z'
        default_version:
            description: The default version.
            returned: always
            type: str
            sample: v1
        description:
            description: The policy description.
            returned: always
            type: str
            sample: OSS administrator
        policy_name:
            description: The policy name.
            returned: always
            type: str
            sample: OSS-Administrator
        name:
            description: alias of 'policy_name'.
            returned: always
            type: str
            sample: OSS-Administrator
        policy_type:
            description: The policy type.
            returned: always
            type: str
            sample: Custom
        update_date:
            description: The date and time when the policy was modified.
            returned: always
            type: str
            sample: '2015-01-23T12:33:18Z'
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.alibaba.apsarastack.plugins.module_utils.apsarastack_common import common_argument_spec
from ansible_collections.alibaba.apsarastack.plugins.module_utils.apsarastack_connections import ram_connect, do_common_request

HAS_FOOTMARK = False

try:
    from footmark.exception import RAMResponseError
    HAS_FOOTMARK = True
except ImportError:
    HAS_FOOTMARK = False


def policy_exists(module, ram_conn, policy_name, policy_id=None):
    if policy_id:
        return True
    params = {
        "policyName": policy_name,
    }
    try:
        response = do_common_request(
            ram_conn, "POST", "ascm", "2019-05-10", "ListRAMPolicies", "/ascm/auth/role/listRAMPolicies", body=params)
        for policy in response["data"]:
            if policy["policyName"] == policy_name:
                return policy
    except Exception as e:

        return module.fail_json(msg="Failed to describe policy: {0}".format(e))
    

def create_ram_policy(module, ram_conn):
    params = {
        "policyName": module.params["policy_name"],
        "policyDocument": module.params['policy_document'],
        "description": module.params['description']
    }
    try:
        do_common_request(
            ram_conn, "POST", "ascm", "2019-05-10", "CreateRAMPolicy", "/ascm/auth/role/createRAMPolicy", body=params)
        return policy_exists(module, ram_conn, module.params["policy_name"])
    except Exception as e:

        return module.fail_json(msg="Failed to create policy: {0}".format(e))
    

def update_ram_policy(module, ram_conn):
    params = {
        "ramPolicyId": module.params["policy_id"]
    }
    if module.params.get("policy_name"):
        params["newPolicyName"] = module.params['policy_name']
    if module.params.get("description"):
        params["newDescription"] = module.params['description']
    try:
        do_common_request(
            ram_conn, "POST", "ascm", "2019-05-10", "UpdateRAMPolicy", "/ascm/auth/role/updateRAMPolicy", body=params)
        return policy_exists(module, ram_conn, module.params["policy_name"])
    except Exception as e:

        return module.fail_json(msg="Failed to update policy: {0}".format(e))
    

def delete_ram_policy(module, ram_conn):
    params = {
        "ramPolicyId": module.params["policy_id"]
    }
    try:
        do_common_request(
            ram_conn, "POST", "ascm", "2019-05-10", "RemoveRAMPolicy", "/ascm/auth/role/removeRAMPolicy", body=params)
        return True
    except Exception as e:
        return module.fail_json(msg="Failed to update policy: {0}".format(e))
    

def remove_role_policy(module, ram_conn):
    params = {"roleId":module.params["role_id"],"ramPolicyId":module.params["policy_id"]}
    try:
        do_common_request(
            ram_conn, "POST", "ascm", "2019-05-10", "RemoveRAMPolicyFromRole", "/ascm/auth/role/removeRAMPolicyFromRole", body=params)
        return True
    except Exception as e:
        return module.fail_json(msg="Failed to remove_role_policy: {0}".format(e))
    
def add_role_policy(module, ram_conn):
    params = {"roleId":module.params["role_id"],"ramPolicyId":module.params["policy_id"]}
    try:
        do_common_request(
            ram_conn, "POST", "ascm", "2019-05-10", "AddRAMPolicyToRole", "/ascm/auth/role/addRAMPolicyToRole", body=params)
        return True
    except Exception as e:
        return module.fail_json(msg="Failed to add_role_policy: {0}".format(e))


def main():
    argument_spec = common_argument_spec()
    argument_spec.update(dict(
        state=dict(default='present', choices=['present', 'absent']),
        policy_document=dict(type='str', aliases=['policy']),
        policy_name=dict(type='str', required=True, aliases=['name']),
        description=dict(type='str'),
        user_name=dict(type='str'),
        group_name=dict(type='str'),
        role_id=dict(type='str'),
        policy_type=dict(type='str', choices=['System', 'Custom'], aliases=['type']),
        policy_id=dict(type='str', aliases=['id']),
    ))

    module = AnsibleModule(argument_spec=argument_spec)

    if HAS_FOOTMARK is False:
        module.fail_json(msg='footmark required for this module.')

    ram_conn = ram_connect(module)

    # Get values of variable
    state = module.params['state']
    policy_name = module.params['policy_name']
    user_name = module.params['user_name']
    group_name = module.params['group_name']
    role_id = module.params['role_id']
    policy_type = module.params['policy_type']
    changed = False

    # Check if policy exists
    policy = policy_exists(module, ram_conn, policy_name)

    if state == 'absent':
        # if user_name:
        #     try:
        #         module.exit_json(changed=policy.detach_policy_from_user(user_name=user_name, policy_type=policy_type), policy=policy.read())
        #     except RAMResponseError as ex:
        #         module.fail_json(msg='Unable to detach policy {0} from user {1}, error: {2}'.format(policy_name, user_name, ex))
        # if group_name:
        #     try:
        #         module.exit_json(changed=policy.detach_policy_from_group(group_name=group_name, policy_type=policy_type), policy=policy.read())
        #     except RAMResponseError as ex:
        #         module.fail_json(msg='Unable to detach policy {0} from group {1}, error: {2}'.format(policy_name, group_name, ex))
        if role_id:
            try:
                module.exit_json(changed=remove_role_policy(module, ram_conn), policy=policy)
            except RAMResponseError as ex:
                module.fail_json(msg='Unable to detach policy {0} from role {1}, error: {2}'.format(policy_name, role_id, ex))
        if not policy:
            module.exit_json(changed=changed, policy={})
        try:
            module.exit_json(changed=delete_ram_policy(module, ram_conn), policy={})
        except RAMResponseError as ex:
            module.fail_json(msg='Unable to delete policy {0}, error: {1}'.format(policy_name, ex))

    if not policy:
        try:
            policy = create_ram_policy(module, ram_conn)
            module.exit_json(changed=True, policy=policy)
        except RAMResponseError as e:
            module.fail_json(msg='Unable to create policy, error: {0}'.format(e))

    # if user_name and policy_type:
    #     try:
    #         changed = policy.attach_policy_to_user(policy_type=policy_type, user_name=user_name)
    #         module.exit_json(changed=changed, policy=policy.read())
    #     except Exception as e:
    #         module.fail_json(msg='Unable to attach policy to user, error: {0}'.format(e))

    # if group_name and policy_type:
    #     try:
    #         changed = policy.attach_policy_to_group(policy_type=policy_type, group_name=group_name)
    #         module.exit_json(changed=changed, policy=policy.read())
    #     except Exception as e:
    #         module.fail_json(msg='Unable to attach policy to group, error: {0}'.format(e))

    if role_id:
        try:
            changed = add_role_policy(module, ram_conn)
            policy = policy_exists(module, ram_conn, policy_name)
            module.exit_json(changed=changed, policy=policy)
        except Exception as e:
            module.fail_json(msg='Unable to attach policy to role, error: {0}'.format(e))
    
    module.exit_json(changed=False, policy=policy)

if __name__ == '__main__':
    main()
