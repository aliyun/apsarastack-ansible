# encoding: utf-8
'''
Created on 2025年3月4日

@author: jingyu.wy
'''

from ansible.module_utils.basic import env_fallback


def common_argument_spec():
    return dict(
        apsarastack_domain=dict(
            aliases=['domain', 'popgw_domain'], no_log=True,
            fallback=(env_fallback, ['APSARASTACK_DOMAIN', 'APSARASTACK_POPGW_DOMAIN'])
        ),
        apsarastack_access_key=dict(
            aliases=['access_key_id', 'access_key'], no_log=True,
            fallback=(env_fallback, ['APSARASTACK_ACCESS_KEY', 'APSARASTACK_ACCESS_KEY'])
        ),
        apsarastack_secret_key=dict(
            aliases=['secret_access_key', 'secret_key'], no_log=True,
            fallback=(env_fallback, ['APSARASTACK_SECRET_KEY', 'APSARASTACK_SECRET_ACCESS_KEY'])
        ),
        apsarastack_security_token=dict(
            aliases=['security_token'], no_log=True,
            fallback=(env_fallback, ['APSARASTACK_SECURITY_TOKEN'])
        ),
        apsarastack_region=dict(
            required=True, aliases=['region', 'region_id'],
            fallback=(env_fallback, ['APSARASTACK_REGION', 'APSARASTACK_REGION_ID'])
        ),
        apsarastack_is_center_region=dict(
            aliases=['is_center_region'],
            fallback=(env_fallback, ['APSARASTACK_IS_CENTER_REGION']), default=True
        ),
        apsarastack_resourcegroupset=dict(
            required=True, aliases=['resourcegroupset', 'resourcegroupset_id', ],
            fallback=(env_fallback, ['APSARASTACK_RESOURCE_GROUP', 'APSARASTACK_RESOURCE_GROUP_ID', 'APSARASTACK_RESOURCE_GROUP_SET'])
        ),
        apsarastack_protocol=dict(
            aliases=['protocol'], fallback=(env_fallback, ['APSARASTACK_PROTOCOL']), default='http'
        ),
        apsarastack_insecure=dict(
            aliases=['insecure'], fallback=(env_fallback, ['APSARASTACK_INSECURE']), default=False
        ),
    )
