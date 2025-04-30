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

from ansible_collections.alibaba.apsarastack.plugins.module_utils.apsarastack_connections import do_common_request

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: ali_route_entry_info
short_description: Gather facts on vrouter of Alibaba Cloud.
description:
     - This module fetches data from the Open API in Apsarastack.
       The module must be called from within the VRouter itself.
options:    
    vrouter_id:
      description:
        - Id of vrouter of vpc
      aliases: ["id"]
      type: str
    route_table_id:
     description:
        - The ID of the route table.
     type: str
author:
    - "He Guimin (@xiaozhu36)"
requirements:
    - "python >= 3.6"
    - "footmark >= 1.15.0"
extends_documentation_fragment:
    - apsarastack
'''

EXAMPLES = '''
# Fetch vrouter details according to setting different filters
- name: Find all route_entrys in the specified vroute
  ali_route_entry_info:
    vrouter_id: '{{ vrouter_id }}'
    
- name: Find all route_entrys in the specified vroute by route table id
  ali_route_entry_info:
    vrouter_id: '{{ vrouter_id }}'
    route_table_id: '{{ route_table_id }}'  

'''

RETURN = '''
vrouter_id:
    description: VRouter id after operating VRouter.
    returned: when success
    type: str
    sample: "vrt-2ze60agfbr2wcyt08jfov"
route_entrys:
    description: Details about the VRouter that were created.
    returned: when success
    type: list
    sample: [
        {
            "destination_cidr_block": "192.168.5.0/28",
            "instance_id": "",
            "next_hop_type": "local",
            "next_hops": {
                "next_hop": []
            },
            
            "route_table_id": "vtb-2ze1rxml89cl782xxxxxx",
            "status": "Available",
            "tags": {},
            "type": "System"
        },
        {
            "destination_cidr_block": "192.168.1.0/24",
            "instance_id": "",
            "next_hop_type": "local",
            "next_hops": {
                "next_hop": []
            },
            
            "route_table_id": "vtb-2ze1rxml89cl782xxxxxx",
            "status": "Available",
            "tags": {},
            "type": "System"
        },
        {
            "destination_cidr_block": "100.64.0.0/10",
            "instance_id": "",
            "next_hop_type": "service",
            "next_hops": {
                "next_hop": []
            },
            "route_table_id": "vtb-2ze1rxml89cl782xxxxxx",
            "status": "Available",
            "tags": {},
            "type": "System"
        }
    ]
total:
    description: The number of all route entries in vrouter.
    returned: when success
    type: int
    sample: 3
'''

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

def get_all_route_tables(module, route_table_id="", vrouter_id="", page=1, page_size=50):
    data = {
        "RouteTableId": route_table_id,
        "VRouterId": vrouter_id,
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

def get_info(route_entry):
    """
        Retrieves route entry information from an route entry
        ID and returns it as a dictionary
    """
    return {
        'destination_cidr_block': route_entry["DestinationCidrBlock"],
        'instance_id': route_entry["InstanceId"],
        'next_hop_type': route_entry["NextHopType"],
        'next_hops': route_entry["NextHops"],
        'route_table_id': route_entry["RouteTableId"],
        'status': route_entry["Status"],
        'tags': {},
        'type': route_entry["Type"],
        'route_entry_id': route_entry["RouteEntryId"],
        'route_entry_name': route_entry["RouteEntryName"]
    }


def main():
    argument_spec = common_argument_spec()
    argument_spec.update(dict(
        vrouter_id=dict(type='str'),
        route_table_id=dict(type='str', required=True, aliases=['id']))
    )
    module = AnsibleModule(argument_spec=argument_spec)

    if HAS_FOOTMARK is False:
        module.fail_json(msg="Package 'footmark' required for this module.")

    result = []
    vrouter_id = module.params['vrouter_id']
    route_table_id = module.params['route_table_id']


    try:
        vpc_conn = vpc_connect(module)

        # list all route entries in vrouter
        if route_table_id:
            route_tables = get_all_route_tables(module, route_table_id, vrouter_id)
            page = 1
            page_size = 50
            route_tables = []
            route_table = None
            while not route_table and len(route_tables) < page_size:
                route_tables = get_all_route_tables(module, route_table_id=route_table_id, page=page, page_size=page_size)
                for rt in route_tables:
                    if rt.get("RouteTableId") == route_table_id:
                        route_table = rt
                page + 1
            vrouter_entries = route_table["RouteEntrys"]["RouteEntry"]
            for vrouter_entry in vrouter_entries:
                result.append(get_info(vrouter_entry))
    except Exception as e:
        module.fail_json(msg="Unable to describe vrouter entries, and got an error: {0}.".format(e))

    module.exit_json(changed=False, vrouter_id=vrouter_id, route_entrys=result, total=len(result))


if __name__ == '__main__':
    main()
