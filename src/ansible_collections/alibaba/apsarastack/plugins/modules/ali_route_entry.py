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

from ansible_collections.alibaba.apsarastack.plugins.module_utils.apsarastack_connections import do_common_request

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = """
---
module: ali_route_entry
short_description: Manage route entry for Apsarastack virtual private cloud,
description:
    - Manage route entry for Apsarastack virtual private cloud.
      Create or Delete route entry in one route table.
options:
  state:
    description:
      -  Whether or not to create, delete route entry.
    choices: ['present', 'absent']
    default: 'present'
    type: str
  router_id:
    description:
      - The ID of virtual router to which route entry belongs.
    required: true
    type: str
  destination_cidrblock:
    description:
      - The destination CIDR or Ip address of route entry. Such as:192.168.0.0/24 or 192.168.0.1.
        There is not the same destination cidr_block in the same route table. It is required when creating route entry.
    aliases: ['dest_cidrblock', 'cidr_block']
    type: str
  nexthop_id:
    description:
      - The next hop ID of route entry. It is required when creating a route entry.
    aliases: ['hop_id']
    type: str
  nexthop_type:
    description:
      - The next hop type of route entry.
    default: 'Instance'
    choices: ['Instance', 'Tunnel', 'HaVip', 'RouterInterface', 'VpnGateway']
    aliases: ['hop_type']
    type: str
  name:
    description:
      - The route entry's name. It is required when modify RouteEntryName.
    aliases: ['route_entry_name']
    type: str
notes:
  - The max items of route entry no more than 48 in the same route table.
  - The destination_cidrblock can't have the same cidr block as vswitch and can't belong to its in the same vpc.
  - The destination_cidrblock can't be 100.64.0.0/10 and can't belong to it.
  - When state is 'list', the parameters 'route_table_id', 'destination_cidrblock' and 'nexthop_id' are optional.
requirements:
    - "python >= 3.6"
    - "footmark >= 1.15.0"
extends_documentation_fragment:
    - apsarastack
author:
  - "He Guimin (@xiaozhu36)"
"""

EXAMPLES = """

# basic provisioning example to create custom route
- name: create route entry
  ali_route_entry:
    destination_cidrblock: '{{ cidr_block }}'
    nexthop_id: '{{ nexthop_id }}'
    router_id: 'XXXXXXXX'


# basic provisioning example to delete custom route
- name: delete route
  ali_route_entry:
    destination_cidrblock: '{{ cidr_block }}'
    nexthop_id: '{{ nexthop_id }}'
    router_id: 'XXXXXXXX'
    state: absent
"""

RETURN = '''

destination_cidrblock:
    description: the destination CIDR block of route entry
    returned: on present and absent
    type: str
    sample: "10.0.14.0/24"

route_entry:
    description: Details about the ecs route entry that was created.
    returned: on present
    type: dict
    sample: {
        "destination_cidrblock": "10.0.14.0/24",
        "nexthop_id": "i-2zejbnp5zv525xxxxxx",
        "nexthop_type": "Instance",
        "route_table_id": "vtb-2zeeokge820zn0kxxxxxx",
        "status": "Available",
        "type": "Custom"
    }

destination_cidrblocks:
    description: the list destination CIDR blocks of route entries in one route table
    returned: on list
    type: list
    sample: ["10.0.14.0/24", "10.0.13.0/24", "100.64.0.0/10"]

"route_entries":
    description: Details about the ecs route entries that were retrieved in one route table.
    returned: on list
    type: list
    sample: [
        {
            "destination_cidrblock": "10.0.14.0/24",
            "nexthop_id": "i-2zejbnp5zv525pxxxxxx",
            "nexthop_type": "Instance",
            "route_table_id": "vtb-2zeeokge820zn0kxxxxxx",
            "status": "Available",
            "type": "Custom"
        },
        {
            "destination_cidrblock": "10.0.13.0/24",
            "nexthop_id": "",
            "nexthop_type": "local",
            "route_table_id": "vtb-2zeeokge820zn0kxxxxxx",
            "status": "Available",
            "type": "System"
        }
    ]
route_table_id:
    description: the ID of route table to which route entry belongs
    returned: on present and absent
    type: str
    sample: "vtb-2zemlj5nscgoicjxxxxxx"
total:
    description: The number of all route entries after retrieving route entry.
    returned: on list
    type: int
    sample: 3
'''

# import module snippets
from ansible.module_utils.basic import AnsibleModule
try:
    from ansible_collections.alibaba.apsarastack.plugins.module_utils.apsarastack_common import common_argument_spec
    from ansible_collections.alibaba.apsarastack.plugins.module_utils.apsarastack_connections import vpc_connect
except ImportError:
    from ..module_utils.apsarastack_common import common_argument_spec
    from ..module_utils.apsarastack_connections import vpc_connect

HAS_FOOTMARK = False

try:
    from footmark.exception import VPCResponseError
    HAS_FOOTMARK = True
except ImportError:
    HAS_FOOTMARK = False


def get_route_entry_detail(route_entry):
    if route_entry:
        return {
            "route_entry_id": route_entry["RouteEntryId"],            
            "destination_cidrblock": route_entry["DestinationCidrBlock"],
            "nexthop_id": route_entry["InstanceId"],
            "nexthop_type": route_entry["NextHopType"],
            "route_table_id": route_entry["RouteTableId"],
            "status": route_entry["Status"],
            "type": route_entry["Type"]
        }

def get_all_route_tables(module, route_table_id="", page=1, page_size=50):
    data = {
        "RouteTableId": route_table_id,
        "PageNumber": page,
        "PageSize": page_size,
    }
    try:
        response = do_common_request(
            vpc_connect(module), "POST", "Vpc", "2016-04-28", "DescribeRouteTables", body=data)
        if response["asapiSuccess"] and response.get("RouteTables"):
            route_tables = response["RouteTables"]["RouteTable"]
            return route_tables
    except VPCResponseError as e:
        module.fail_json(msg='Failed to get route entry, error: {0}'.format(e))

def do_create_route_entry(module, route_entry_params):
    try:
        # print(route_entry_params)
        response = do_common_request(
            vpc_connect(module), "POST", "Vpc", "2016-04-28", "CreateRouteEntry", body=route_entry_params)
        if response["asapiSuccess"]:
            return True
    except VPCResponseError as e:
        module.fail_json(msg='Failed to create route entry, error: {0}'.format(e))

def do_delete_route_entry(module, route_entry):
    data = {
        "RouteEntryId": route_entry["route_entry_id"],
        "DestinationCidrBlock": route_entry["destination_cidrblock"],
        "NextHopId": route_entry["nexthop_id"],
        "RouteTableId": route_entry["route_table_id"],
    }
    try:
        response = do_common_request(
            vpc_connect(module), "POST", "Vpc", "2016-04-28", "DeleteRouteEntry", body=data)
        if response["asapiSuccess"]:
            return True
    except VPCResponseError as e:
        module.fail_json(msg='Failed to create route entry, error: {0}'.format(e))

def do_get_route_entry(module, route_table_id, destination_cidrblock):
    try:
        page = 1
        page_size = 50
        route_entry = None
        route_tables = []
        route_table = None
        destination_cidrblock = module.params['destination_cidrblock']
        while not route_table and len(route_tables) < page_size:
            route_tables = get_all_route_tables(module, route_table_id=route_table_id, page=page, page_size=page_size)
            for rt in route_tables:
                if rt.get("RouteTableId") == route_table_id:
                    route_table = rt
            page + 1
        
        for re in route_table["RouteEntrys"]["RouteEntry"]:
            if re.get("DestinationCidrBlock") == destination_cidrblock:
                route_entry = get_route_entry_detail(re)
                break
        return route_entry
    except AttributeError as e:
        module.fail_json(msg='Failed to create route entry, error: {0}, route_tables: {1}'.format(e, route_tables))
    except VPCResponseError as e:
        module.fail_json(msg='Failed to create route entry, error: {0}'.format(e))

def create_route_entry(module):
    """
    Create VSwitch
    :param module: Ansible module object
    :param vpc: Authenticated vpc connection object
    :return: Return details of created VSwitch
    """
    destination_cidrblock = module.params['destination_cidrblock']
    nexthop_type = module.params['nexthop_type']
    nexthop_id = module.params['nexthop_id']
    route_table_id = module.params['route_table_id']
    route_entry_name = module.params['name']

    if not nexthop_id:
        module.fail_json(msg='nexthop_id is required for creating a route entry.')

    if not destination_cidrblock:
        module.fail_json(msg='destination_cidrblock is required for creating a route entry.')

    try:
        route_entry_params = {
            'RouteTableId': route_table_id, 
            'NextHopType': nexthop_type, 
            'NextHopId': nexthop_id, 
            "DestinationCidrBlock": destination_cidrblock,
            "RouteEntryName": route_entry_name
        }
        if do_create_route_entry(module, route_entry_params):
            route_entry = do_get_route_entry(module, route_table_id, destination_cidrblock)
            if route_entry:
                return route_entry
    except VPCResponseError as e:
        module.fail_json(msg='Unable to create route entry, error: {0}'.format(e))


def main():
    argument_spec = common_argument_spec()
    argument_spec.update(dict(
        state=dict(default='present', choices=['present', 'absent']),
        destination_cidrblock=dict(type='str', aliases=['dest_cidrblock', 'cidr_block']),
        nexthop_type=dict(default='Instance', aliases=['hop_type'], choices=['Instance', 'Tunnel', 'HaVip', 'RouterInterface', 'VpnGateway']),
        nexthop_id=dict(aliases=['hop_id']),
        route_table_id=dict(type='str', required=True),
        router_id=dict(aliases=['route_entry_id']),
        name=dict(aliases=['route_entry_name']),
    ))

    module = AnsibleModule(argument_spec=argument_spec)

    if HAS_FOOTMARK is False:
        module.fail_json(msg='footmark required for the module ali_route_entry.')

    # Get values of variable
    state = module.params['state']
    name = module.params['name']
    route_entry = None
    if str(name).startswith('http://') or str(name).startswith('https://'):
        module.fail_json(msg='router_entry_name can not start with http:// or https://')

    changed = False
    if state == 'present':
        try:
            route_entry = create_route_entry(module)
            module.exit_json(changed=False, route_entry=route_entry)
        except VPCResponseError as e:
            module.fail_json(msg='failed to create route entry {0}, error: {1}'.format(route_entry["route_entry_id"], e))

    else:
        if route_entry:
            try:
                if do_delete_route_entry(module, route_entry):
                    module.exit_json(changed=False, route_entry={})
            except VPCResponseError as e:
                module.fail_json(msg='failed to delete route entry, error: {0}'.format(e))

        module.exit_json(changed=changed, msg="Please specify a route entry by using 'destination_cidrblock', and "
                                              "expected ""vpcs: {0}".format({"route_table_id": route_entry["route_table_id"],
                                                                             "destination_cidrblock": route_entry["destination_cidrblock"]}))
    return 


if __name__ == '__main__':
    main()
