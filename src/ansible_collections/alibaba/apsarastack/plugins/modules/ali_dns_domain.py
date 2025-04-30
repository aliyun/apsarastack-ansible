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

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.alibaba.apsarastack.plugins.module_utils.apsarastack_common import common_argument_spec
from ansible_collections.alibaba.apsarastack.plugins.module_utils.apsarastack_connections import dns_connect, do_common_request

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = """
---
module: ali_dns_domain
short_description: Configure Alibaba Cloud DNS (DNS)
description:
    - Create, Delete Apsarastack cloud DNS(DNS).
      It supports updating DNS remark and change domain group.
options:
  domain_name:
    description:
      -  The name to give your DNS.
    required: True
    aliases: ['name']
    type: str
  group_name:
    description:
      - Specify name of group, when change domain group.
    type: str
  lang:
    description:
      - The language which you choose
    type: str
  resource_group_id:
    description:
      - When add domain, You can specify the resource group id.
    type: str
  remark:
    description:
      - Specify this parameter as a comment for dns.
    type: str
  state:
    description:
      -  Whether or not to create, delete DNS.
    choices: ['present', 'absent']
    default: 'present'
    type: str
  user_client_ip:
    description:
      - User client IP.
    type: str
requirements:
    - "python >= 3.6"
    - "footmark >= 1.15.0"
extends_documentation_fragment:
    - apsarastack
author:
  - "He Guimin (@xiaozhu36)"
"""

EXAMPLES = """
# Note: These examples do not set authentication details, see the Alibaba Cloud Guide for details.
- name: Create a new domain
  ali_dns_domain:
    state: 'present'
    domain_name: '{{ domain_name }}'
    remark: '{{ remark }}'

- name: Changed. Changed. Modify remark.
  ali_dns_domain:
    domain_name: '{{ domain_name }}'
    remark: 'new--{{ remark }}'

- name: Changed. change domain group.
  ali_dns_domain:
    domain_name: '{{ domain_name }}'
    group_name: '{{ group_name }}'

- name: Changed. Deleting dns
  ali_dns_domain:
    domain_name: '{{ domain_name }}'
    state: absent
"""

RETURN = '''
dns:
    description: info about the DNS that was created or deleted.
    returned: always
    type: complex
    contains:
        ali_domain:
            description: Whether it is the domain name of Alibaba Cloud.
            returned: always
            type: bool
            sample: false
        dns_servers:
            description: The DNS list of the domain name in the resolution system.
            returned: always
            type: dict
            sample: 
                dns_servers:
                    dns_server: 
                     - xx1.alidns.com
                     - xx2.alidns.com

        domain_name:
            description: The name of domain.
            returned: always
            type: str
            sample: ansiblexxx.abc
        name:
            description: alias of 'domain_name'.
            returned: always
            type: str
            sample: ansiblexxx.abc
        id:
            description: alias of 'domain_id'.
            returned: always
            type: str
            sample: dns-c2xxxxxx
        puny_code:
            description: Chinese domain name punycode code, English domain name returned empty.
            type: bool
            sample: ansiblexxx.abc
        record_count:
            description: The number of parsing records contained in the domain name.
            returned: always
            type: int
            sample: 0
        remark:
            description: A comment for dns.
            returned: always
            type: str
            sample: ansible_test_dns_domain
        starmark:
            description: Whether to query the domain name star.
            returned: always
            type: bool
            sample: false
        domain_id:
            description: DNS resource id.
            returned: always
            type: str
            sample: dns-c2xxxxxx
        version_code:
            description: Cloud resolution version Code.
            returned: always
            type: str
            sample: mianfei
        version_name:
            description: Cloud resolution product name.
            returned: always
            type: str
            sample: Alibaba Cloud DNS
'''
HAS_FOOTMARK = False

try:
    from footmark.exception import DNSResponseError
    HAS_FOOTMARK = True
except ImportError:
    HAS_FOOTMARK = False


def dns_exists_v2(module, dns_conn, domain_name=None, domain_id=None):
    if not domain_name and not domain_id:
        return False
    try:
        i = 1
        params = {
            "PageNumber": i,
            "PageSize": 10,
        }
        response = do_common_request(
            dns_conn, "POST", "CloudDns", "2021-06-24", "DescribeGlobalZones", body=params)
        for domain in response["Data"]:
            if domain_name:
                if domain["Name"] == domain_name:
                    return domain
            else:
                if domain["Id"] == domain_id:
                    return domain
        while response["Data"] and (i-1) * params["PageSize"] + len(response["Data"]) < response["TotalItems"]:
            i += 1
            params = {
                "PageNumber": i,
                "PageSize": 10,
            }
            response = do_common_request(
                dns_conn, "POST", "CloudDns", "2021-06-24", "DescribeGlobalZones", body=params)
            for domain in response["Data"]:
                if domain_name:
                    if domain["Name"] == domain_name:
                        return domain
                else:
                    if domain["Id"] == domain_id:
                        return domain
    except Exception as e:
        module.fail_json(msg="Failed to dns_exists_v2: {0}".format(e))


def describe_dns(module, dns_conn, dns_id):
    return dns_exists_v2(module, dns_conn, domain_id=dns_id)


def add_domains_v2(module, dns_conn, params):
    try:
        response = do_common_request(
            dns_conn, "POST", "CloudDns", "2021-06-24", "AddGlobalZone", body=params)
        if response["asapiSuccess"]:
            domain_id = response["Id"]
            return describe_dns(module, dns_conn, domain_id)
    except Exception as e:
        module.fail_json(
            msg="Failed to add_domains_v2: %s  params: %s" % (e, params))


def dns_delete_v2(module, dns_conn, dns_id):
    params = {
        "Id": dns_id
    }
    try:
        response = do_common_request(
            dns_conn, "POST", "CloudDns", "2021-06-24", "DeleteGlobalZone", body=params)
        if response["asapiSuccess"]:
            return True
    except Exception as e:
        module.fail_json(msg="Failed to dns_delete_v2: {0}".format(e))


def modify_remark_v2(module, dns_conn, dns_name, dns_remark):
    dns = dns_exists_v2(module, dns_conn, dns_name)
    params = {
        "Id": dns["Id"],
        "Name": dns_name,
        "Remark": dns_remark
    }
    try:
        do_common_request(dns_conn, "POST", "CloudDns",
                          "2021-06-24", "UpdateGlobalZoneRemark", body=params)
        return describe_dns(module, dns_conn, dns["Id"])
    except Exception as e:
        module.fail_json(msg="Failed to modify_remark_v2: {0}".format(e))


def dns_exists(module, dns_conn, domain_name):
    """Returns None or a vpc object depending on the existence of a VPC. When supplied
    with a CIDR and Name, it will check them to determine if it is a match
    otherwise it will assume the VPC does not exist and thus return None.
    """
    matching_dns = []
    try:
        for v in dns_conn.describe_domains():
            if v.domain_name == domain_name:
                matching_dns.append(v)
    except Exception as e:
        module.fail_json(msg="Failed to describe DNSs: {0}".format(e))

    if matching_dns:
        return matching_dns[0]


def main():
    argument_spec = common_argument_spec()
    argument_spec.update(dict(
        domain_name=dict(type='str', aliases=['name'], required=True),
        group_name=dict(type='str'),
        lang=dict(type='str'),
        resource_group_id=dict(type='str'),
        remark=dict(type='str'),
        state=dict(default='present', choices=['present', 'absent']),
        user_client_ip=dict(type='str')
    ))

    module = AnsibleModule(argument_spec=argument_spec)

    if HAS_FOOTMARK is False:
        module.fail_json(
            msg='footmark required for the module ali_dns_domain.')

    dns_conn = dns_connect(module)

    # Get values of variable
    state = module.params['state']
    domain_name = module.params['domain_name']
    remark = module.params['remark']
    group_name = module.params['group_name']
    changed = False

    # Check if VPC exists
    dns = dns_exists_v2(module, dns_conn, domain_name)

    if state == 'absent':
        if not dns:
            module.exit_json(changed=changed, dns={})
        try:
            dns_id = dns["Id"]
            dns_delete_v2(module, dns_conn, dns_id)
            module.exit_json(changed=True, dns={})
        except DNSResponseError as ex:
            module.fail_json(
                msg='Unable to delete dns {0}, error: {1}'.format(dns.id, ex))

    if not dns:
        params = module.params
        params_add = {"Name": params["domain_name"]}
        try:
            dns = add_domains_v2(module, dns_conn, params_add)
            if dns:
                changed = False
        except DNSResponseError as e:
            module.fail_json(msg='Unable to create dns, error: {0}'.format(e))

    # if domain_name and group_name:
    #     try:
    #         res = dns.change_domain_group(group_name=group_name, domain_name=domain_name)
    #         if res:
    #             changed = True
    #     except DNSResponseError as e:
    #         module.fail_json(msg='Unable to change domain group, error: {0}'.format(e))

    if remark:
        try:
            dns = modify_remark_v2(
                module, dns_conn, module.params["domain_name"], remark)
            if dns:
                changed = True
        except DNSResponseError as e:
            module.fail_json(
                msg='Unable to modify dns remark, error: {0}'.format(e))
    module.exit_json(changed=changed, dns=dns)


if __name__ == '__main__':
    main()
