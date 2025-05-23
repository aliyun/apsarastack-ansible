#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017-present Alibaba Group Holding Limited. He Guimin <heguimin36@163.com.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
#  This file is part of Ansible
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

DOCUMENTATION = '''
---
module: ali_ram_user_info
short_description: Gather info on ram users in Alibaba Cloud.
description:
     - Gather info on ram users in Alibaba Cloud. support name_prefix to filter users.
options:
  name_prefix:
    description:
      - Use a User name prefix to filter Users.
    type: str
  user_ids:
    description:
      - Use a user_ids list to filter Users.
    type: list
    elements: str
author:
    - "He Guimin (@xiaozhu36)"
requirements:
    - "python >= 3.6"
    - "footmark >= 1.17.0"
extends_documentation_fragment:
    - apsarastack
'''

EXAMPLES = '''
# Note: These examples do not set authentication details, see the Alibaba Cloud Guide for details.

- name: Get infos about all Users
  ali_ram_user_info:

- name: Get infos about a particular User using name_prefix
  ali_ram_user_info:
    name_prefix: "ansible"

'''

RETURN = '''
users:
    description: Returns an array of complex objects as described below.
    returned: always
    type: complex
    contains:
        user_name:
            description: The username.
            returned: always
            type: str
            sample: Alice
        name:
            description: alias of 'user_name'.
            returned: always
            type: str
            sample: Alice
        user_id:
            description: The ID of the RAM user.
            returned: always
            type: str
            sample: 122748924538****
        id:
            description: alias of 'user_id'.
            returned: always
            type: str
            sample: 122748924538****
        update_date:
            description: The date and time when the user information was modified.
            returned: always
            type: str
            sample: '2015-01-23T12:33:18Z'
        mobile_phone:
            description: The mobile phone number of the RAM user.
            returned: always
            type: str
            sample: 86-1860000****
        phone:
            description: alias of 'mobile_phone'.
            returned: always
            type: str
            sample: vpc-c2e00da5
        email:
            description: The email address of the RAM user.
            returned: always
            type: str
            sample: alice@example.com
        display_name:
            description: The display name.
            returned: always
            type: str
            sample: Alice
        create_date:
            description: The date and time when the RAM user was created.
            returned: always
            type: str
            sample: '2015-01-23T12:33:18Z'
        comments:
            description: The comment.
            returned: always
            type: str
            sample: ansible test
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.alibaba.apsarastack.plugins.module_utils.apsarastack_connections import ram_connect, do_common_request
from ansible_collections.alibaba.apsarastack.plugins.module_utils.apsarastack_common import common_argument_spec
from ansible_collections.alibaba.apsarastack.plugins.modules.ali_ram_user import user_exists
HAS_FOOTMARK = False

try:
    from footmark.exception import RAMResponseError
    HAS_FOOTMARK = True
except ImportError:
    HAS_FOOTMARK = False

def user_list(module, ram_conn, user_name=None, display_name=None, user_id=None):
    params = {}
    if user_name:
        params["searchKey"] = user_name
    if display_name:
        params["displayName"] = display_name
    if user_id:
        params["primaryKey"] = user_id
    try:
        response = do_common_request(
            ram_conn, "POST", "ascm", "2019-05-10", "ListUsers", "/ascm/auth/user/listUsers", body=params)
        return response["data"]

    except Exception as e:

        return module.fail_json(msg="Failed to describe Users: {0}".format(e))

def main():
    argument_spec = common_argument_spec()
    argument_spec.update(dict(
        name_prefix=dict(type='str')),
        display_name_prefix=dict(type='str'),
        user_ids=dict(type='list', elements='str')
    )
    module = AnsibleModule(argument_spec=argument_spec)

    if HAS_FOOTMARK is False:
        module.fail_json(msg="Package 'footmark' required for this module.")
    ram_conn = ram_connect(module)

    name_prefix = module.params['name_prefix']
    user_ids = module.params['user_ids']
    display_name = module.params['display_name_prefix']
    try:
        if user_ids:
            users = []
            for user_id in user_ids:
                user = user_list(module, ram_conn, user_id=user_id)
                users += user
        else:
            users = user_list(module, ram_conn, user_name=name_prefix, display_name=display_name)
        module.exit_json(changed=False, users=users)
    except Exception as e:
        module.fail_json(msg=str("Unable to list users, error:{0}".format(e)))


if __name__ == '__main__':
    main()
