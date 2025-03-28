#!/usr/bin/python
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
import json

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = """
---
module: ali_slb_tag
short_description: Add tags for Alibaba Cloud SLB resource.
description:
    - Add tags to Alibaba Cloud SLB resources
options:
  state:
    description:
      -  Whether or not to add, remove tags.
    choices: ['present', 'absent']
    default: 'present'
  resource_id:
    description:
      - id of slb.
    elements: str
  resource_type:
    description:
      - The type of SLB resource.
    default: 'instance'
  tags:
    description:
      - A hash/dictionaries of resource tags. C({"key":"value"})
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
- name: Changed. Add Tags.
  ali_slb_tag:
    resource_type: 'instance'
    resource_id: lb_id
    tags: {
            "Ansible": "Add tags"
    }

- name: Changed. Remove Tags.
  ali_slb_tag:
    state: absent
    resource_type: 'instance'
    resource_id: lb_id
    tags: {
      "Ansible": "Add tags"
    }
"""

RETURN = '''
tags:
    description:
      - info about the server load balancer that was added tags.
    returned: always
    type: complex
    contains:
        tags:
            description: Tags of resource.
            returned: always
            type: dict
            sample: {"tag_key": "tag_value"}
'''


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.alibaba.apsarastack.plugins.module_utils.apsarastack_common import common_argument_spec
from ansible_collections.alibaba.apsarastack.plugins.module_utils.apsarastack_connections import do_common_request, slb_connect

HAS_FOOTMARK = False

try:
    from footmark.exception import SLBResponseError
    HAS_FOOTMARK = True
except ImportError:
    HAS_FOOTMARK = False

def tags_to_json(tags):
    tags_dict = {}
    for tagkey, tagvalue in tags.items():
        tags_dict["TagKey"] = tagkey
        tags_dict["TagValue"] = tagvalue
    return json.dumps(tags_dict)

def tag_resources(module, resource_id, tags, resource_type):
    try:
        data = {
            "LoadBalancerId": resource_id,
            "ResourceType": resource_type,
            "Tags": tags_to_json(tags)
        }
        response = do_common_request(
            slb_connect(module), "POST", "Slb", "2014-05-15", "AddTags", body=data)
        if response["asapiSuccess"]:
            return True
    except Exception as e:
        print("=========================================data: %s" % data)
        module.fail_json(msg='Failed to create route entry, error: {0}'.format(e))


def untag_resources(module, resource_id, tags, resource_type):
    try:
        data = {
            "LoadBalancerId": resource_id,
            "ResourceType": resource_type,
            "Tags": tags_to_json(tags)
        }
        response = do_common_request(
            slb_connect(module), "POST", "Slb", "2014-05-15", "RemoveTags", body=data)
        if response["asapiSuccess"]:
            return True
    except Exception as e:
        module.fail_json(msg='Failed to create route entry, error: {0}'.format(e))

def list_tags(module, resource_id, resource_type):
    try:
        data = {
            "LoadBalancerId": resource_id,
            "ResourceType": resource_type
        }
        # print(route_entry_params)
        response = do_common_request(
            slb_connect(module), "POST", "ascm", "2014-05-15", "DescribeTags", body=data)
        if response["asapiSuccess"]:
            tags = dict()
            tags_dict = response["TagSets"]["TagSet"]
            for tag in tags_dict:
                tags["TagKey"] = tags["TagValue"]
            return tags
    except SLBResponseError as e:
        module.fail_json(msg='Failed to create route entry, error: {0}'.format(e))


def main():
    argument_spec = common_argument_spec()
    argument_spec.update(dict(
        state=dict(default='present', choices=['present', 'absent']),
        resource_id=dict(type='str'),
        resource_type=dict(type='str', default='slb_instance'),
        tags=dict(type='dict')
    ))

    module = AnsibleModule(argument_spec=argument_spec)

    if HAS_FOOTMARK is False:
        module.fail_json(msg='footmark required for the module ali_slb_tag.')

    # slb_conn = slb_connect(module)

    # Get values of variable
    tags = module.params['tags']

    if module.params['state'] == "present":
        slb_changed = tag_resources(module, resource_id=module.params['resource_id'], tags=tags, resource_type=module.params['resource_type'])
        tags = list_tags(module, resource_id=module.params['resource_id'], resource_type=module.params['resource_type'])
    else:
        slb_changed = untag_resources(module, resource_id=module.params['resource_id'], tags=tags, resource_type=module.params['resource_type'])

    result = []
    # for slb in slbs:
    #     result.append(slb.get().read())

    module.exit_json(changed=slb_changed, tags=result)


if __name__ == '__main__':
    main()
