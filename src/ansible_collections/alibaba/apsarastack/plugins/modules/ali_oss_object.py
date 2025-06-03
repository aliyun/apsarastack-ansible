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
module: ali_oss_object
version_added: "1.5.0"
short_description: Manage object in OSS
description:
    - This module allows the user to manage OSS objects within bucket. Includes support for uploading and downloading
      objects, retrieving object keys.
options:
  mode:
    description:
      - Switches the module behaviour between put (upload), get (download), list (list objects) and delete (delete object).
    required: true
    choices: ['get', 'put', 'delete', 'list']
  bucket:
    description:
      - Bucket name.
    required: true
  permission:
    description:
      - This option lets the user set the canned permissions on the objects that are put. The permissions that
        can be set are 'private', 'public-read', 'public-read-write'.
    default: 'private'
    choices: [ 'private', 'public-read', 'public-read-write' ]
    aliases: [ 'acl' ]
  headers:
    description:
      - Custom headers for PUT or GET operation, as a dictionary of 'key=value' and 'key=value,key=value'.
  overwrite:
    description:
      - Force overwrite specified object content when putting object.
        If it is true/false, object will be normal/appendable. Appendable Object can be convert to Noraml by setting
        overwrite to true, but conversely, it won't be work.
    default: False
    type: bool
  content:
    description:
      - The object content that will be upload. It is conflict with 'file_name' when mode is 'put'.
  file_name:
    description:
      - The name of file that used to upload or download object.
    aliases: [ "file" ]
  object:
    description:
      - Name to object after uploaded to bucket
    required: true
    aliases: [ 'key', 'object_name' ]
  byte_range:
    description:
      - The range of object content that would be download.
        Its format like 1-100 that indicates range from one to hundred bytes of object.
    aliases: [ 'range' ]
requirements:
    - "python >= 2.6"
    - "footmark >= 1.1.16"
extends_documentation_fragment:
    - apsarastack
author:
  - "He Guimin (@xiaozhu36)"
'''

EXAMPLES = '''

# basic provisioning example to upload a content
- name: simple upload to bucket
  hosts: localhost
  connection: local
  vars:
    apsarastack_access_key: <your-apsarastack-access-key-id>
    apsarastack_secret_key: <your-apsarastack-access-secret-key>
    apsarastack_region: cn-hangzhou
    mode: put
    bucket: bucketname
    content: 'Hello world! I come from apsarastack.'
    object: 'remote_file.txt'
    headers:
      Content-Type: 'text/html'
      Content-Encoding: md5
  tasks:
    - name: simple upload to bucket
      ali_oss_object:
        apsarastack_access_key: '{{ apsarastack_access_key }}'
        apsarastack_secret_key: '{{ apsarastack_secret_key }}'
        apsarastack_region: '{{ apsarastack_region }}'
        mode: '{{ mode }}'
        bucket: '{{ bucket }}'
        content: '{{ content }}'
        headers: '{{ headers }}'
      register: result
    - debug: var=result

# basic provisioning example to upload a file
- name: simple upload to bucket
  hosts: localhost
  connection: local
  vars:
    apsarastack_access_key: <your-apsarastack-access-key-id>
    apsarastack_secret_key: <your-apsarastack-access-secret-key>
    apsarastack_region: cn-hangzhou
    mode: put
    bucket: bucketname
    file_name: 'test_oss.yml'
    object: 'remote_file.txt'
    headers:
      Content-Type: 'text/html'
      Content-Encoding: md5
  tasks:
    - name: simple upload to bucket
      ali_oss_object:
        apsarastack_access_key: '{{ apsarastack_access_key }}'
        apsarastack_secret_key: '{{ apsarastack_secret_key }}'
        apsarastack_region: '{{ apsarastack_region }}'
        mode: '{{ mode }}'
        file_name: '{{ file_name }}'
        content: '{{ content }}'
        headers: '{{ headers }}'
      register: result
    - debug: var=result

# basic provisioning example to download a object
- name: simple upload to bucket
  hosts: localhost
  connection: local
  vars:
    apsarastack_access_key: <your-apsarastack-access-key-id>
    apsarastack_secret_key: <your-apsarastack-access-secret-key>
    apsarastack_region: cn-hangzhou
    mode: get
    bucket: bucketname
    download: 'my_test.json'
    byte_range: 0-100
    object: 'remote_file.txt'
    headers:
      Content-Type: 'text/html'
      Content-Encoding: md5
  tasks:
    - name: simple upload to bucket
      ali_oss_object:
        apsarastack_access_key: '{{ apsarastack_access_key }}'
        apsarastack_secret_key: '{{ apsarastack_secret_key }}'
        apsarastack_region: '{{ apsarastack_region }}'
        mode: '{{ mode }}'
        file_name: '{{ download }}'
        byte_range: '{{ byte_range }}'
        content: '{{ content }}'
        headers: '{{ headers }}'
      register: result
    - debug: var=result

# basic provisioning example to list bucket objects
- name: list bucket objects
  hosts: localhost
  connection: local
  vars:
    apsarastack_access_key: <your-apsarastack-access-key-id>
    apsarastack_secret_key: <your-apsarastack-access-secret-key>
    apsarastack_region: cn-hangzhou
    mode: list
    bucket: bucketname
  tasks:
    - name: list bucket objects
      ali_oss_object:
        apsarastack_access_key: '{{ apsarastack_access_key }}'
        apsarastack_secret_key: '{{ apsarastack_secret_key }}'
        apsarastack_region: '{{ apsarastack_region }}'
        mode: '{{ mode }}'
        bucket: '{{ bucket }}'
      register: list_result
    - debug: var=list_result

# basic provisioning example to delete bucket object
- name: delete bucket objects
  hosts: localhost
  connection: local
  vars:
    apsarastack_access_key: <your-apsarastack-access-key-id>
    apsarastack_secret_key: <your-apsarastack-access-secret-key>
    apsarastack_region: cn-hangzhou
    mode: delete
    bucket: bucketname
    object: 'remote_file.txt'
  tasks:
    - name: delete bucket objects
      ali_oss_object:
        apsarastack_access_key: '{{ apsarastack_access_key }}'
        apsarastack_secret_key: '{{ apsarastack_secret_key }}'
        apsarastack_region: '{{ apsarastack_region }}'
        mode: '{{ mode }}'
        bucket: '{{ bucket }}'
        object: '{{ object }}'
      register: delete_object_result
    - debug: var=delete_object_result
'''

RETURN = '''
changed:
    description: current operation whether changed the resource
    returned: when success
    type: bool
    sample: true
key:
    description: the name of oss object
    returned: expect list
    type: bool
    sample: true
object:
    description: the object's information
    returned: on put or get
    type: dict
    sample: {
        "etag": "A57B09D4A76BCF486DDD755900000000",
        "key": "newobject-2",
        "last_modified": "2017-07-24 19:43:41",
        "next_append_position": 11,
        "size": "11 B",
        "storage_class": "Standard",
        "type": "Appendable"
    }
objects:
    description: the list all objects that has the prefix of 'object' value in the specified bucket
    returned: when list
    type: list
    sample: [
        {
            "etag": "54739B1D5AEBFD38C83356D8A8A3EDFC",
            "key": "newobject-1",
            "last_modified": "2017-07-24 19:42:46",
            "size": "2788 B",
            "storage_class": "Standard",
            "type": "Normal"
        },
        {
            "etag": "EB8BDADA044D58D58CDE755900000000",
            "key": "newobject-2",
            "last_modified": "2017-07-24 19:48:28",
            "next_append_position": 5569,
            "size": "5569 B",
            "storage_class": "Standard",
            "type": "Appendable"
        }
    ]
'''
# import module snippets
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.alibaba.apsarastack.plugins.module_utils.apsarastack_common import common_argument_spec
from ansible_collections.alibaba.apsarastack.plugins.module_utils.apsarastack_connections import ossbucket_connect, ossbucket_object_conn, do_asapi_common_request, ossservice_connect
import time
import json
import oss2

HAS_FOOTMARK = False

try:
    from footmark.exception import ECSResponseError, OSSResponseError
    HAS_FOOTMARK = True
except ImportError:
    HAS_FOOTMARK = False

def put_bucket_object(module, oss_conn):
    params = {
        "BucketName":module.params['bucket'],
        "ObjectName": module.params['object']
        }
    query = {
        "OpenApiAction": "PutObject",
        "ProductName": "oss"
    }
    query["Params"] = json.dumps(params)
    try:
        do_asapi_common_request(
            oss_conn, "POST", "OneRouter", "2018-12-12", "DoOpenApi", query=query)
        return is_object_exist(module, oss_conn)
    except Exception as e:

        return module.fail_json(msg="Failed to create_bucket: {0}".format(e))
    

def is_object_exist(module, oss_conn, max_keys=None):
    params = {
        "BucketName":module.params['bucket'],
        "delimiter": "/",
        "encoding-type": "url"
        }
    if module.params.get('object'):
        params["prefix"] = module.params['object']
    if max_keys:
        params["max-keys"] = max_keys
    query = {
        "OpenApiAction": "GetBucket",
        "ProductName": "oss"
    }
    query["Params"] = json.dumps(params)
    try:
        response = do_asapi_common_request(
            oss_conn, "POST", "OneRouter", "2018-12-12", "DoOpenApi", query=query)
        if "Contents" in response["Data"]["ListBucketResult"]:
            return response["Data"]["ListBucketResult"]["Contents"]
    except Exception as e:

        return module.fail_json(msg="Failed to create_bucket: {0}".format(e))
    

def put_object_acl(module, oss_conn):
    params = {
        "BucketName":module.params['bucket'],
        "ObjectName": module.params['object'],
        "x-oss-object-acl": module.params['permission']
        }
    query = {
        "OpenApiAction": "PutObjectACL",
        "ProductName": "oss"
    }
    query["Params"] = json.dumps(params)
    try:
        do_asapi_common_request(
            oss_conn, "POST", "OneRouter", "2018-12-12", "DoOpenApi", query=query)
    except Exception as e:

        return module.fail_json(msg="Failed to put_object_acl: {0}".format(e))

def delete_object(module, oss_conn):
    try:
      auth = oss2.Auth(oss_conn.acs_access_key_id, oss_conn.acs_secret_access_key)
      bucket = oss2.Bucket(auth, oss_conn._endpoint, module.params['bucket'])
      bucket.batch_delete_objects([module.params['object']])
    except Exception as e:
      module.fail_json(msg="Failed to delete_object: {0}".format(e))

def put_object_from_file(module, oss_conn):
    try:
      auth = oss2.Auth(oss_conn.acs_access_key_id, oss_conn.acs_secret_access_key)
      bucket = oss2.Bucket(auth, oss_conn._endpoint, module.params['bucket'])
      remote_file = module.params['object'] + module.params['file_name']
      bucket.put_object_from_file(remote_file, module.params['file_name'])
    except Exception as e:
      module.fail_json(msg="Failed to put_object_from_file: {0}".format(e))


def get_object_acl(module, oss_conn):
    params = {
        "BucketName":module.params['bucket'],
        "ObjectName": module.params['object']
        }
    query = {
        "OpenApiAction": "GetObjectACL",
        "ProductName": "oss"
    }
    query["Params"] = json.dumps(params)
    try:
        response = do_asapi_common_request(
            oss_conn, "POST", "OneRouter", "2018-12-12", "DoOpenApi", query=query)
        return response["Data"]["AccessControlPolicy"]["AccessControlList"]["Grant"]
    except Exception as e:
        module.fail_json(msg="Failed to get_object_acl: {0}".format(e))
    


def main():
    argument_spec = common_argument_spec()
    argument_spec.update(dict(
        bucket=dict(type='str', required=True),
        mode=dict(type='str', required=True, choices=['put', 'get', 'list', 'delete']),
        permission=dict(type='str', default='private', choices=['private', 'public-read', 'public-read-write']),
        headers=dict(type='dict'),
        overwrite=dict(type='bool', default=False),
        content=dict(type='str'),
        file_name=dict(type='str', aliases=['file']),
        object=dict(type='str', aliases=['key', 'object_name']),
        byte_range=dict(type='str', aliases=['range']),
    )
    )
    module = AnsibleModule(argument_spec=argument_spec)

    if HAS_FOOTMARK is False:
        module.fail_json(msg="Package 'footmark' required for the module ali_oss_object.")

    oss_conn = ossbucket_connect(module)
    oss_service_conn = ossservice_connect(module)
    mode = module.params['mode']
    file_name = module.params['file_name']
    object_key = module.params['object']
    headers = module.params['headers']

    changed = True

    if mode == 'put':
        content = module.params['content']
        if content and file_name:
            module.fail_json(msg="'content' and 'file_name' only one can be specified when mode is put.")

        overwrite = module.params['overwrite']
        permission = module.params['permission']

        try:
            bucket_object = is_object_exist(module, oss_conn)
            if not bucket_object:
                bucket_object = put_bucket_object(module, oss_conn)
                changed = False
            elif file_name:
                put_object_from_file(module, oss_service_conn)
                changed = True
            if permission and changed and not module.params['object'].endswith('/'):
                put_object_acl(module, oss_conn)
                changed = get_object_acl(module, oss_conn)
                # changed = True
            # if headers:
            #     oss_bucket.update_object_headers(object_key, headers)
                # changed = True
            module.exit_json(changed=changed, key=object_key, object=bucket_object)
        except Exception as e:
            module.fail_json(msg="Unable to upload an object {0} or "
                                 "modify its permission and headers, and got an error: {1}".format(object_key, e))

    elif mode == 'get':
        pass
        # byte_range = module.params['byte_range']
        # try:
        #     if file_name:
        #         oss_bucket.get_object_to_file(object_key, file_name, byte_range=byte_range, headers=headers)
        #     else:
        #         module.fail_json(msg="'file_name' must be specified when mode is get.")
        #     module.exit_json(changed=changed, key=object_key, object=get_object_info(oss_bucket.get_object_info(object_key)))
        # except Exception as e:
        #     module.fail_json(msg="Unable to download object {0}, and got an error: {1}".format(object_key, e))

    elif mode == 'list':
        objects = []
        max_keys = 500
        try:
            while True:
                results = is_object_exist(module, oss_conn, max_keys)

                if len(results) < max_keys:
                    break
            module.exit_json(changed=False, objects=results)
        except Exception as e:
            module.fail_json(msg="Unable to retrieve all objects, and got an error: {0}".format(e))

    else:
        try:
            delete_object(module, oss_service_conn)
            module.exit_json(changed=changed, key=object_key)
        except Exception as e:
            module.fail_json(msg="Unable to delete an object {0}, and got an error: {1}".format(object_key, e))


if __name__ == '__main__':
    main()
