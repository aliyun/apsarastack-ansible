#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017-present Alibaba Group Holding Limited. He Guimin <heguimin36@163.com>
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
module: ali_instance_info
short_description: Gather information on instances of Alibaba Cloud ECS.
description:
     - This module fetches data from the Open API in Apsarastack.
       The module must be called from within the ECS instance itself.
     - This module was called C(ali_instance_facts) before Ansible 2.9. The usage did not change.

options:
    availability_zone:
      description:
        - (Deprecated) Aliyun availability zone ID in which to launch the instance. Please use filter item 'zone_id' instead.
      aliases: ['apsarastack_zone']
      type: str
    instance_names:
      description:
        - (Deprecated) A list of ECS instance names. Please use filter item 'instance_name' instead.
      aliases: ["names"]
      type: list
      elements: str
    instance_ids:
      description:
        - A list of ECS instance ids.
      aliases: ["ids"]
      type: list
      elements: str
    name_prefix:
      description:
        - Use a instance name prefix to filter ecs instances.
      type: str
    tags:
      description:
        - A hash/dictionaries of instance tags. C({"key":"value"})
      aliases: ["instance_tags"]
      type: dict
    filters:
      description:
        - A dict of filters to apply. Each dict item consists of a filter key and a filter value. The filter keys can be
          all of request parameters. See U(https://www.alibabacloud.com/help/doc-detail/25506.htm) for parameter details.
          Filter keys can be same as request parameter name or be lower case and use underscore ("_") or dash ("-") to
          connect different words in one parameter. 'InstanceIds' should be a list and it will be appended to
          I(instance_ids) automatically. 'Tag.n.Key' and 'Tag.n.Value' should be a dict and using I(tags) instead.
      type: dict
author:
    - "He Guimin (@xiaozhu36)"
requirements:
    - "python >= 3.6"
    - "footmark >= 1.13.0"
extends_documentation_fragment:
    - apsarastack
'''

EXAMPLES = '''
# Fetch instances details according to setting different filters

- name: Find all instances in the specified region
  ali_instance_info:
  register: all_instances

- name: Find all instances based on the specified ids
  ali_instance_info:
    instance_ids:
      - "i-35xxxxxx"
      - "i-ddxxxxxx"
  register: instances_by_ids

- name: Find all instances based on the specified name_prefix
  ali_instance_info:
    name_prefix: "ecs_instance_"
  register: instances_by_name_prefix

- name: Find instances based on tags
  ali_instance_info:
    tags:
      Test: "add"
'''

RETURN = '''
instances:
    description: List of ECS instances
    returned: always
    type: complex
    contains:
        availability_zone:
            description: The availability zone of the instance is in.
            returned: always
            type: str
            sample: cn-beijing-a
        block_device_mappings:
            description: Any block device mapping entries for the instance.
            returned: always
            type: complex
            contains:
                device_name:
                    description: The device name exposed to the instance (for example, /dev/xvda).
                    returned: always
                    type: str
                    sample: /dev/xvda
                attach_time:
                    description: The time stamp when the attachment initiated.
                    returned: always
                    type: str
                    sample: "2018-06-25T04:08:26Z"
                delete_on_termination:
                    description: Indicates whether the volume is deleted on instance termination.
                    returned: always
                    type: bool
                    sample: true
                status:
                    description: The attachment state.
                    returned: always
                    type: str
                    sample: in_use
                volume_id:
                    description: The ID of the cloud disk.
                    returned: always
                    type: str
                    sample: d-2zei53pjsi117y6gf9t6
        cpu:
            description: The CPU core count of the instance.
            returned: always
            type: int
            sample: 4
        creation_time:
            description: The time the instance was created.
            returned: always
            type: str
            sample: "2018-06-25T04:08Z"
        description:
            description: The instance description.
            returned: always
            type: str
            sample: "my ansible instance"
        eip:
            description: The attribution of EIP associated with the instance.
            returned: always
            type: complex
            contains:
                allocation_id:
                    description: The ID of the EIP.
                    returned: always
                    type: str
                    sample: eip-12345
                internet_charge_type:
                    description: The internet charge type of the EIP.
                    returned: always
                    type: str
                    sample: "paybybandwidth"
                ip_address:
                    description: EIP address.
                    returned: always
                    type: str
                    sample: 42.10.2.2
        expired_time:
            description: The time the instance will expire.
            returned: always
            type: str
            sample: "2099-12-31T15:59Z"
        gpu:
            description: The attribution of instance GPU.
            returned: always
            type: complex
            contains:
                amount:
                    description: The count of the GPU.
                    returned: always
                    type: int
                    sample: 0
                spec:
                    description: The specification of the GPU.
                    returned: always
                    type: str
                    sample: ""
        host_name:
            description: The host name of the instance.
            returned: always
            type: str
            sample: iZ2zewaoZ
        id:
            description: Alias of instance_id.
            returned: always
            type: str
            sample: i-abc12345
        instance_id:
            description: ECS instance resource ID.
            returned: always
            type: str
            sample: i-abc12345
        image_id:
            description: The ID of the image used to launch the instance.
            returned: always
            type: str
            sample: m-0011223344
        instance_charge_type:
            description: The instance charge type.
            returned: always
            type: str
            sample: PostPaid
        instance_name:
            description: The name of the instance.
            returned: always
            type: str
            sample: my-ecs
        instance_type_family:
            description: The instance type family of the instance belongs.
            returned: always
            type: str
            sample: ecs.sn1ne
        instance_type:
            description: The instance type of the running instance.
            returned: always
            type: str
            sample: ecs.sn1ne.xlarge
        internet_charge_type:
            description: The billing method of the network bandwidth.
            returned: always
            type: str
            sample: PayByBandwidth
        internet_max_bandwidth_in:
            description: Maximum incoming bandwidth from the internet network.
            returned: always
            type: int
            sample: 200
        internet_max_bandwidth_out:
            description: Maximum incoming bandwidth from the internet network.
            returned: always
            type: int
            sample: 20
        io_optimized:
            description: Indicates whether the instance is optimized for EBS I/O.
            returned: always
            type: bool
            sample: false
        memory:
            description: Memory size of the instance.
            returned: always
            type: int
            sample: 8192
        network_interfaces:
            description: One or more network interfaces for the instance.
            returned: always
            type: complex
            contains:
                mac_address:
                    description: The MAC address.
                    returned: always
                    type: str
                    sample: "00:11:22:33:44:55"
                network_interface_id:
                    description: The ID of the network interface.
                    returned: always
                    type: str
                    sample: eni-01234567
                primary_ip_address:
                    description: The primary IPv4 address of the network interface within the vswitch.
                    returned: always
                    type: str
                    sample: 10.0.0.1
        osname:
            description: The operation system name of the instance owned.
            returned: always
            type: str
            sample: CentOS
        ostype:
            description: The operation system type of the instance owned.
            returned: always
            type: str
            sample: linux
        private_ip_address:
            description: The IPv4 address of the network interface within the subnet.
            returned: always
            type: str
            sample: 10.0.0.1
        public_ip_address:
            description: The public IPv4 address assigned to the instance or eip address
            returned: always
            type: str
            sample: 43.0.0.1
        resource_group_id:
            description: The id of the resource group to which the instance belongs.
            returned: always
            type: str
            sample: my-ecs-group
        security_groups:
            description: One or more security groups for the instance.
            returned: always
            type: list
            elements: dict
            contains:
                group_id:
                  description: The ID of the security group.
                  returned: always
                  type: str
                  sample: sg-0123456
                group_name:
                  description: The name of the security group.
                  returned: always
                  type: str
                  sample: my-security-group
        status:
            description: The current status of the instance.
            returned: always
            type: str
            sample: running
        tags:
            description: Any tags assigned to the instance.
            returned: always
            type: dict
            sample:
        vswitch_id:
            description: The ID of the vswitch in which the instance is running.
            returned: always
            type: str
            sample: vsw-dew00abcdef
        vpc_id:
            description: The ID of the VPC the instance is in.
            returned: always
            type: str
            sample: vpc-0011223344
ids:
    description: List of ECS instance IDs
    returned: always
    type: list
    sample: [i-1xxxxxx, i-3xxxxxx]
'''

import traceback
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible_collections.alibaba.apsarastack.plugins.module_utils.apsarastack_common import common_argument_spec
from ansible_collections.alibaba.apsarastack.plugins.module_utils.apsarastack_connections import ecs_connect

HAS_FOOTMARK = False
FOOTMARK_IMP_ERR = None
try:
    from footmark.exception import ECSResponseError
    HAS_FOOTMARK = True
except ImportError:
    FOOTMARK_IMP_ERR = traceback.format_exc()
    HAS_FOOTMARK = False


def main():
    argument_spec = common_argument_spec()
    argument_spec.update(dict(
        availability_zone=dict(aliases=['apsarastack_zone']),
        instance_ids=dict(type='list', elements='str', aliases=['ids']),
        instance_names=dict(type='list', elements='str', aliases=['names']),
        name_prefix=dict(type='str'),
        tags=dict(type='dict', aliases=['instance_tags']),
        filters=dict(type='dict')
    )
    )
    module = AnsibleModule(argument_spec=argument_spec)
    if module._name == 'ali_instance_facts':
        module.deprecate("The 'ali_instance_facts' module has been renamed to 'ali_instance_info'", version='2.13')

    if HAS_FOOTMARK is False:
        module.fail_json(msg=missing_required_lib('footmark'), exception=FOOTMARK_IMP_ERR)

    ecs = ecs_connect(module)

    instances = []
    instance_ids = []
    ids = module.params['instance_ids']
    name_prefix = module.params['name_prefix']
    names = module.params['instance_names']
    zone_id = module.params['availability_zone']
    if ids and (not isinstance(ids, list) or len(ids) < 1):
        module.fail_json(msg='instance_ids should be a list of instances, aborting')

    if names and (not isinstance(names, list) or len(names) < 1):
        module.fail_json(msg='instance_names should be a list of instances, aborting')

    filters = module.params['filters']
    if not filters:
        filters = {}
    if not ids:
        ids = []
    for key, value in list(filters.items()):
        if key in ["InstanceIds", "instance_ids", "instance-ids"] and isinstance(ids, list):
            for id in value:
                if id not in ids:
                    ids.append(value)
    if ids:
        filters['instance_ids'] = ids
    if module.params['tags']:
        filters['tags'] = module.params['tags']
    if zone_id:
        filters['zone_id'] = zone_id
    if names:
        filters['instance_name'] = names[0]

    for inst in ecs.describe_instances(**filters):
        if name_prefix:
            if not str(inst.instance_name).startswith(name_prefix):
                continue
        volumes = ecs.describe_disks(instance_id=inst.id)
        setattr(inst, 'block_device_mappings', volumes)
        setattr(inst, 'user_data', inst.describe_user_data())
        instances.append(inst.read())
        instance_ids.append(inst.id)

    module.exit_json(changed=False, ids=instance_ids, instances=instances)


if __name__ == '__main__':
    main()
