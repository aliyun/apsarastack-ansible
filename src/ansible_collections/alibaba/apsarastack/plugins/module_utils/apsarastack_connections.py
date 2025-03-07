# encoding: utf-8
'''
Created on 2025年3月4日

@author: jingyu.wy
'''
import json
import os
import types

from footmark.connection import ACSQueryConnection

try:
    import footmark
    import footmark.ecs
    import footmark.slb
    import footmark.vpc
    import footmark.rds
    import footmark.ess
    import footmark.sts
    import footmark.dns
    import footmark.ram
    import footmark.ros
    import footmark.oos
    import footmark.market
    HAS_FOOTMARK = True
except ImportError:
    HAS_FOOTMARK = False

APSARASTACK_ENDPOINTS = {
    "vpc": ("vpc-internal.%(domain)s", "vpc-internal.%(region)s.%(domain)s",)
    }


class AnsibleACSError(Exception):
    pass


def get_acs_connection_info(params):

    return dict(
        acs_access_key_id=params.get('apsarastack_access_key'),
        acs_secret_access_key=params.get('apsarastack_secret_key'),
        security_token=params.get('apsarastack_security_token'),
        ecs_role_name=params.get('ecs_role_name'),
        user_agent='Ansible-Provider-Apsarastack',
    )


def get_assume_role(params):
    """ Return new params """
    sts_params = get_acs_connection_info(params)
    assume_role = {}
    if params.get('assume_role'):
        assume_role['apsarastack_assume_role_arn'] = params['assume_role'].get('role_arn')
        assume_role['apsarastack_assume_role_session_name'] = params['assume_role'].get('session_name')
        assume_role['apsarastack_assume_role_session_expiration'] = params['assume_role'].get('session_expiration')
        assume_role['apsarastack_assume_role_policy'] = params['assume_role'].get('policy')

    assume_role_params = {
        'role_arn': params.get('apsarastack_assume_role_arn') if params.get('apsarastack_assume_role_arn') else assume_role.get('apsarastack_assume_role_arn'),
        'role_session_name': params.get('apsarastack_assume_role_session_name') if params.get('apsarastack_assume_role_session_name')
        else assume_role.get('apsarastack_assume_role_session_name'),
        'duration_seconds': params.get('apsarastack_assume_role_session_expiration') if params.get('apsarastack_assume_role_session_expiration')
        else assume_role.get('apsarastack_assume_role_session_expiration', 3600),
        'policy': assume_role.get('apsarastack_assume_role_policy', {})
    }

    try:
        sts = connect_to_acs(footmark.sts, params.get('apsarastack_region'), **sts_params).assume_role(**assume_role_params).read()
        sts_params['acs_access_key_id'], sts_params['acs_secret_access_key'], sts_params['security_token'] \
 = sts['access_key_id'], sts['access_key_secret'], sts['security_token']
    except AnsibleACSError as e:
        params.fail_json(msg=str(e))
    return sts_params


def get_profile(params):
    if not params['apsarastack_access_key'] and not params['ecs_role_name'] and params['profile']:
        path = params['shared_credentials_file'] if params['shared_credentials_file'] else os.getenv('HOME') + '/.apsarastack/config.json'
        auth = {}
        with open(path, 'r') as f:
            for pro in json.load(f)['profiles']:
                if params['profile'] == pro['name']:
                    auth = pro
        if auth:
            if auth['mode'] == 'AK' and auth.get('access_key_id') and auth.get('access_key_secret'):
                params['apsarastack_access_key'] = auth.get('access_key_id')
                params['apsarastack_secret_key'] = auth.get('access_key_secret')
                params['apsarastack_region'] = auth.get('region_id')
                params = get_acs_connection_info(params)
            elif auth['mode'] == 'StsToken' and auth.get('access_key_id') and auth.get('access_key_secret') and auth.get('sts_token'):
                params['apsarastack_access_key'] = auth.get('access_key_id')
                params['apsarastack_secret_key'] = auth.get('access_key_secret')
                params['security_token'] = auth.get('sts_token')
                params['apsarastack_region'] = auth.get('region_id')
                params = get_acs_connection_info(params)
    elif params.get('apsarastack_assume_role_arn') or params.get('assume_role'):
        params = get_assume_role(params)
    else:
        params = get_acs_connection_info(params)
    return params


def get_endpoint(domain:str, popcode:str, region:str, is_center_region:bool) -> str:
    index = 0 if is_center_region else 1
    endpoint_template = APSARASTACK_ENDPOINTS[popcode][index]
    return endpoint_template % {"domain":domain, "region":region}


def connect_to_acs(acs_module, modules_params:dict, **params):
    conn = acs_module.connect_to_region(modules_params['apsarastack_region'], **params)
    popcode = acs_module.__name__.split('.')[-1]
    endpoint = get_endpoint(
        modules_params['apsarastack_domain'], popcode,
        modules_params['apsarastack_region'], modules_params['apsarastack_is_center_region'])

    def import_request(self, action):
        request = ACSQueryConnection.import_request(self, action)
        request.set_endpoint(endpoint)
        request.set_headers({
            "x-acs-organizationid": modules_params['apsarastack_department'],
            "x-acs-resourcegroupid": modules_params['apsarastack_resourcegroup'],
            "x-acs-regionid": modules_params['apsarastack_region'],
            "x-acs-request-version": "v1",
        })
        return request
    
    conn.import_request = types.MethodType(import_request, conn)

    return conn



def ecs_connect(module):
    """ Return an ecs connection"""
    ecs_params = get_profile(module.params)
    # If we have a region specified, connect to its endpoint.
    region = module.params.get('apsarastack_region')
    if region:
        try:
            ecs = connect_to_acs(footmark.ecs, region, **ecs_params)
        except AnsibleACSError as e:
            module.fail_json(msg=str(e))
    # Otherwise, no region so we fallback to the old connection method
    return ecs


def vpc_connect(module):
    """ Return an vpc connection"""
    vpc_params = get_profile(module.params)
    # If we have a region specified, connect to its endpoint.
    try:
        vpc = connect_to_acs(footmark.vpc, module.params, **vpc_params)
    except AnsibleACSError as e:
        module.fail_json(msg=str(e))
    # Otherwise, no region so we fallback to the old connection method
    return vpc
