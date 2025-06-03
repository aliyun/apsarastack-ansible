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

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: ali_oss_bucket
version_added: "2.4"
short_description: Create/Delete/Retrieve Bucket.
description:
    - This module allows the user to manage OSS buckets. Includes support for creating, deleting and retrieving buckets.
options:
  state:
    description:
      - Create or delete the OSS bucket. List all buckets that has the prefix of 'bucket' value.
    default: 'present'
    choices: [ 'present', 'absent', 'list']
  bucket:
    description:
      - Bucket name.
    required: true
    aliases: [ 'name' ]
  permission:
    description:
      - This option lets the user set the canned permissions on the bucket that are created.
    default: 'private'
    choices: [ 'private', 'public-read', 'public-read-write' ]
    aliases: [ 'acl' ]
requirements:
    - "python >= 2.6"
    - "footmark >= 1.1.16"
extends_documentation_fragment:
    - apsarastack
author:
  - "He Guimin (@xiaozhu36)"
'''

EXAMPLES = '''
#
# provisioning new oss bucket
#

# basic provisioning example to create bucket
- name: create oss bucket
  hosts: localhost
  connection: local
  vars:
    apsarastack_access_key: <your-apsarastack-access-key-id>
    apsarastack_secret_key: <your-apsarastack-access-secret-key>
    apsarastack_region: cn-hangzhou
    state: present
    bucket: bucketname
    permission: public-read-write
  tasks:
    - name: create oss bucket
      ali_oss_bucket:
        apsarastack_access_key: '{{ apsarastack_access_key }}'
        apsarastack_secret_key: '{{ apsarastack_secret_key }}'
        apsarastack_region: '{{ apsarastack_region }}'
        state: '{{ state }}'
        bucket: '{{ bucket }}'
        permission: '{{ permission }}'
      register: result
    - debug: var=result

# basic provisioning example to delete bucket
- name: delete oss bucket
  hosts: localhost
  connection: local
  vars:
    apsarastack_access_key: <your-apsarastack-access-key-id>
    apsarastack_secret_key: <your-apsarastack-access-secret-key>
    apsarastack_region: cn-hangzhou
    state: absent
    bucket: bucketname
  tasks:
    - name: delete oss bucket
      ali_oss_bucket:
        apsarastack_access_key: '{{ apsarastack_access_key }}'
        apsarastack_secret_key: '{{ apsarastack_secret_key }}'
        apsarastack_region: '{{ apsarastack_region }}'
        state: '{{ state }}'
        bucket: '{{ bucket }}'
      register: result
    - debug: var=result
'''

RETURN = '''
changed:
    description: current operation whether changed the resource
    returned: when success
    type: bool
    sample: true
bucket:
    description: the bucket's headers after create bucket or update its acl
    returned: on present
    type: dict
    sample: {
        "id": "dsadasd",
        "location": "oss-cn-beijing",
        "name": "xiaozhubucket",
        "permission": "public-read"
    }
buckets:
    description: the list all buckets that has the prefix of 'bucket' value in the specified region
    returned: when list
    type: list
    sample: [
        {
            "id": "dasd",
            "location": "oss-cn-beijing",
            "name": "xiaozhubucket",
            "permission": "public-read"
        },
        {
            "id": "dasdsad-2",
            "location": "oss-cn-beijing",
            "name": "xiaozhubucket-2",
            "permission": "private"
        }
    ]
'''

# import module snippets
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.alibaba.apsarastack.plugins.module_utils.apsarastack_common import common_argument_spec
from ansible_collections.alibaba.apsarastack.plugins.module_utils.apsarastack_connections import ossbucket_connect, ossservice_connect, do_asapi_common_request
import json

HAS_FOOTMARK = False

try:
    from footmark.exception import ECSResponseError, OSSResponseError
    HAS_FOOTMARK = True
except ImportError:
    HAS_FOOTMARK = False


def get_bucket(module, oss_conn):
    params = {
        "OpenApiAction": "GetBucketInfo",
        "ProductName": "oss"
    }
    query = {
            "BucketName": module.params['bucket_name']
        }
    query["Params"] = json.dumps(params)
    try:
        response = do_asapi_common_request(
            oss_conn, "POST", "OneRouter", "2018-12-12", "DoOpenApi", query=params)
        module.fail_json(msg=response)
    except Exception as e:

        return module.fail_json(msg="Failed to get_bucket: {0}".format(e))

def exist_bucket(module, oss_conn):
    params = {
        "OpenApiAction": "GetService",
        "ProductName": "oss"
    }
    try:
        response = do_asapi_common_request(
            oss_conn, "POST", "OneRouter", "2018-12-12", "DoOpenApi", query=params)
        buckets = response["Data"]["ListAllMyBucketsResult"]["Buckets"]["Bucket"]
        for bucket in buckets:
            if bucket['Name'] == module.params['bucket_name']:
                return bucket
    except Exception as e:

        return module.fail_json(msg="Failed to exist_bucket: {0}".format(e))
    
def put_acl(module, oss_conn):
    params = {
        "BucketName":module.params['bucket_name'],
        "x-oss-acl":module.params['permission']
        }
    query = {
        "OpenApiAction": "PutBucketACL",
        "ProductName": "oss"
    }
    query["Params"] = json.dumps(params)
    try:
        response = do_asapi_common_request(
            oss_conn, "POST", "OneRouter", "2018-12-12", "DoOpenApi", query=query)
    except Exception as e:

        return module.fail_json(msg="Failed to put_acl: {0}".format(e))
    

def get_acl(module, oss_conn):
    params = {
        "BucketName":module.params['bucket_name'],
        "acl":"acl"
        }
    query = {
        "OpenApiAction": "GetBucketAcl",
        "ProductName": "oss"
    }
    query["Params"] = json.dumps(params)
    try:
        response = do_asapi_common_request(
            oss_conn, "POST", "OneRouter", "2018-12-12", "DoOpenApi", query=query)
        return response["data"]
    except Exception as e:

        return module.fail_json(msg="Failed to get_acl: {0}".format(e))
    

def create_bucket(module, oss_conn):
    params = {
        "BucketName":module.params['bucket_name']
        }
    if module.params.get('permission'):
        params["x-oss-acl"] = module.params['permission']
    query = {
        "OpenApiAction": "PutBucket",
        "ProductName": "oss"
    }
    query["Params"] = json.dumps(params)
    try:
        do_asapi_common_request(
            oss_conn, "POST", "OneRouter", "2018-12-12", "DoOpenApi", query=query)
        return exist_bucket(module, oss_conn)
    except Exception as e:

        return module.fail_json(msg="Failed to create_bucket: {0}".format(e))
    

def delete_bucket(module, oss_conn):

    params = {
        "BucketName":module.params['bucket_name']
        }
    if module.params.get('permission'):
        params["x-oss-acl"] = module.params['permission']
    query = {
        "OpenApiAction": "DeleteBucket",
        "ProductName": "oss"
    }
    query["Params"] = json.dumps(params)
    try:
        cc = do_asapi_common_request(
            oss_conn, "POST", "OneRouter", "2018-12-12", "DoOpenApi", query=query)
        return exist_bucket(module, oss_conn)
    except Exception as e:

        return module.fail_json(msg="Failed to delete_bucket: {0}".format(e))



def main():
    argument_spec = common_argument_spec()  
    argument_spec.update(
        dict(
            state=dict(required=True, choices=['present', 'absent', 'list']),
            permission=dict(default='private', choices=['private', 'public-read', 'public-read-write'], aliases=['acl']),
            bucket_name=dict(required=True, aliases=["name"]),
        )
    )
    module = AnsibleModule(argument_spec=argument_spec)

    if HAS_FOOTMARK is False:
        module.fail_json(msg="Package 'footmark' required for the module ali_oss_bucket.")

    state = module.params['state']
    permission = module.params['permission']
    oss_conn = ossbucket_connect(module)
    oss_service_conn = ossservice_connect(module)

    if state == 'present':
        try:
            if exist_bucket(module, oss_conn):
                result = put_acl(module, oss_conn)  
            else:
                result = create_bucket(module, oss_conn)
            module.exit_json(changed=True, bucket=exist_bucket(module, oss_conn))
        except Exception as e:
            module.fail_json(msg="Unable to put bucket or set acl for it, and got an error: {0}.".format(e))

    elif state == 'absent':
        try:
            delete_bucket(module, oss_conn)
            module.exit_json(changed=True)
        except Exception as e:
            module.fail_json(msg="Unable to delete bucket, and got an error: {0}.".format(e))

    else:
        try:
            oss_service = ossservice_connect(module)
            keys = oss_service.list_buckets(prefix=module.params['bucket'], max_keys=200)

            buckets = []
            for name in keys:
                module.params['bucket_name'] = name
                buckets.append(exist_bucket(module, oss_conn))

            module.exit_json(changed=False, buckets=buckets)
        except Exception as e:
            module.fail_json(msg="Unable to list buckets, and got an error: {0}.".format(e))


if __name__ == '__main__':
    main()
