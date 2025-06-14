# encoding: utf-8
'''
Created on 2025年3月4日

@author: jingyu.wy
'''
import json
import os
import types

from aliyunsdkcore.auth.credentials import AccessKeyCredential,\
    StsTokenCredential
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
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
    import footmark.oss
    import footmark.market
    HAS_FOOTMARK = True
except ImportError:
    HAS_FOOTMARK = False

APSARASTACK_ENDPOINTS = {
    "vpc": ("vpc-internal.%(domain)s", "vpc-internal.%(region)s.%(domain)s",),
    "ecs": ("ecs-internal.%(domain)s", "ecs-internal.%(region)s.%(domain)s",),
    "dns": ("dns-control.pop.%(domain)s", "dns-control.pop.%(region)s.%(domain)s",),
    "rds": ("rds.%(domain)s", "rds.%(region)s.%(domain)s",),
    "slb": ("slb-vpc.%(domain)s", "slb-vpc.%(region)s.%(domain)s",),
    "ascm": ("ascm.%(domain)s", "ascm.%(region)s.%(domain)s",),
    "ess": ("ess.%(domain)s", "ess.%(region)s.%(domain)s",),
    "ram": ("ascm.%(domain)s", "ascm.%(region)s.%(domain)s",),
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
    conn._endpoint = get_endpoint(
        modules_params['apsarastack_domain'], popcode,
        modules_params['apsarastack_region'], modules_params['apsarastack_is_center_region']
    )
    conn._default_headers = {
        "x-acs-organizationid": modules_params['apsarastack_department'],
        "x-acs-resourcegroupid": modules_params['apsarastack_resourcegroup'],
        "x-acs-regionid": modules_params['apsarastack_region'],
        "x-acs-request-version": "v1",
		# "RegionId":              client.RegionId, //	ASAPI
		# "x-acs-organizationid":  client.Department,
		# "x-acs-resourcegroupid": client.ResourceGroup,
		# "x-acs-regionid":        client.RegionId,
		# "x-acs-request-version": "v1",
		# "x-acs-asapi-product":   popcode,
		# "x-ascm-product-name":   popcode,
    }
    def import_request(self, action):
        request = ACSQueryConnection.import_request(self, action)
        request.set_endpoint(conn._endpoint)
        request.set_headers(conn._default_headers)
        return request
    
    conn.import_request = types.MethodType(import_request, conn)

    return conn


def connect_oss_object(ossbucket, modules_params:dict, bucket_name, popcode=None, **params):
    oss_params = get_acs_connection_info(params)
    oss_object = ossbucket(acs_access_key_id=modules_params['apsarastack_access_key'], acs_secret_access_key=modules_params['apsarastack_secret_key'],
                 region=modules_params['apsarastack_region'], bucket_name=bucket_name, security_token=modules_params["apsarastack_security_token"], user_agent=oss_params["user_agent"])
    # conn = acs_module.connect_to_region(modules_params['apsarastack_region'], **params)
    # popcode = acs_module.__name__.split('.')[-1] if not popcode else popcode
    # conn._endpoint = get_endpoint(
    #     modules_params['apsarastack_domain'], popcode,
    #     modules_params['apsarastack_region'], modules_params['apsarastack_is_center_region']
    # )
    # conn._default_headers = {
    #     "x-acs-organizationid": modules_params['apsarastack_department'],
    #     "x-acs-resourcegroupid": modules_params['apsarastack_resourcegroup'],
    #     "x-acs-regionid": modules_params['apsarastack_region'],
    #     "x-acs-request-version": "v1",
	# 	# "RegionId":              client.RegionId, //	ASAPI
	# 	# "x-acs-organizationid":  client.Department,
	# 	# "x-acs-resourcegroupid": client.ResourceGroup,
	# 	# "x-acs-regionid":        client.RegionId,
	# 	# "x-acs-request-version": "v1",
	# 	# "x-acs-asapi-product":   popcode,
	# 	# "x-ascm-product-name":   popcode,
    # }
    # def import_request(self, action):
    #     request = ACSQueryConnection.import_request(self, action)
    #     request.set_endpoint(conn._endpoint)
    #     request.set_headers(conn._default_headers)
    #     return request
    
    # conn.import_request = types.MethodType(import_request, conn)

    return oss_object


class OssConn(object):
  def __init__(self, modules_params):
      self.region = modules_params.get('region')
      self.security_token = modules_params.get('security_token')
      self.acs_access_key_id = modules_params.get('acs_access_key_id')
      self.acs_secret_access_key = modules_params.get('acs_secret_access_key')
      self.user_agent = modules_params.get('user_agent')
def connect_to_bucket(acs_module, modules_params:dict, **params):
    conn = OssConn(params)
    popcode = acs_module.__name__.split('.')[-1]
    conn._endpoint = modules_params["apsarastack_asapi_endpoint"]
    conn._default_headers = {
        "x-acs-organizationid": modules_params['apsarastack_department'],
        "x-acs-resourcegroupid": modules_params['apsarastack_resourcegroup'],
        "x-acs-regionid": modules_params['apsarastack_region'],
        "x-acs-request-version": "v1",
    }
    def import_request(self, action):
        request = ACSQueryConnection.import_request(self, action)
        request.set_endpoint(conn._endpoint)
        request.set_headers(conn._default_headers)
        return request
    
    conn.import_request = types.MethodType(import_request, conn)

    return conn


def connect_to_bucket_service(acs_module, modules_params:dict, **params):
    conn = OssConn(params)
    popcode = "ossservice"
    conn._endpoint = modules_params["apsarastack_ossservice_endpoint"]
    conn._default_headers = {
        "x-acs-organizationid": modules_params['apsarastack_department'],
        "x-acs-resourcegroupid": modules_params['apsarastack_resourcegroup'],
        "x-acs-regionid": modules_params['apsarastack_region'],
        "x-acs-request-version": "v1",
    }
    def import_request(self, action):
        request = ACSQueryConnection.import_request(self, action)
        request.set_endpoint(conn._endpoint)
        request.set_headers(conn._default_headers)
        return request
    
    conn.import_request = types.MethodType(import_request, conn)

    return conn

def connect_to_universal(popcode, modules_params:dict, **params):
    conn = ACSQueryConnection(region=modules_params['apsarastack_region'], **params)
    popcode = "ascm"
    conn._endpoint = get_endpoint(
        modules_params['apsarastack_domain'], popcode,
        modules_params['apsarastack_region'], modules_params['apsarastack_is_center_region']
    )
    conn._default_headers = {
        "x-acs-organizationid": modules_params['apsarastack_department'],
        "x-acs-resourcegroupid": modules_params['apsarastack_resourcegroup'],
        "x-acs-regionid": modules_params['apsarastack_region'],
        "x-acs-request-version": "v1",
    }

    def import_request(self, action):
        request = ACSQueryConnection.import_request(self, action)
        request.set_endpoint(conn._endpoint)
        request.set_headers(conn._default_headers)
        return request
    
    conn.import_request = types.MethodType(import_request, conn)

    return conn


def do_common_request(conn, method:str, popcode: str, version:str, api_name:str, pattern:str="", headers:dict={}, query:dict={}, body:dict=None, data:dict=None) -> dict:
    if not conn.security_token: 
        credentials = AccessKeyCredential(conn.acs_access_key_id, conn.acs_secret_access_key)
    else:
        credentials = StsTokenCredential(conn.acs_access_key_id, conn.acs_secret_access_key, conn.security_token)
    # 创建AcsClient连接,timeout设置请求超时时间(单位：ms)
    client = AcsClient(region_id=conn.region, credential=credentials, timeout=10000)
    # 创建API请求
    request = CommonRequest()
    # 产品接口信息参数
    request.set_product(popcode)
    request.set_version(version)
    request.set_action_name(api_name)
    if pattern:
        request.set_uri_pattern(pattern)
    # 云产品的Endpoint地址
    request.set_domain(conn._endpoint)
    request.set_endpoint(conn._endpoint)
    # 设置请求方式
    request.set_method(method)
    # 设置请求协议类型
    request.set_protocol_type('http')
    
    # 阿里云核心库SDK发起API请求时，可以设置四种类型参数（Path/Query/Body/Header）
    # Path参数用于对请求Request中设置的UriPattern进行变量替换
    # Query参数用于对请求Request中的URL参数进行设置（一般用于GET请求）
    # Body参数用于对请求Request中的HTTP Content进行设置（一般用于POST/PUT请求），在设置Body参数时，需要同时设置HTTP Content-Type，目前支持JSON和FORM两种格式
    # Header参数用于对请求Request中的HTTP Header进行设置
    
    # 设置Headers
    # 设置身份标识,标识调用来源,无实际作用,可随意设置,必填项
    for k, v in conn._default_headers.items():
        request.add_header(k ,v)
    for k, v in headers.items():
        request.add_header(k ,v)

    request.add_header("x-acs-caller-sdk-source", conn.user_agent)
    request.add_header("x-acs-asapi-product", popcode)
    request.add_header("x-ascm-product-name", popcode)
    request.add_header("RegionId", conn.region)
		# "RegionId":              client.RegionId, //	ASAPI
		# "x-acs-organizationid":  client.Department,
		# "x-acs-resourcegroupid": client.ResourceGroup,
		# "x-acs-regionid":        client.RegionId,
    request.set_user_agent(conn.user_agent)
    
    if query:
        query["RegionId"] = request.get_headers()["x-acs-regionid"]
        query["Department"] = request.get_headers()["x-acs-organizationid"]
        query["OrganizationId"] = request.get_headers()["x-acs-organizationid"]
        query["ResourceGroup"] = request.get_headers()["x-acs-resourcegroupid"]
        request.set_query_params(query)
    if body:
        request.set_content_type('application/x-www-form-urlencoded')
        
        request.set_body_params(body)
    if data:
        request.set_content_type('application/json')
        request.set_content(data)
    
    response = client.do_action_with_exception(request)
    
    return json.loads(response)


def do_asapi_common_request(conn, method:str, popcode: str, version:str, api_name:str, pattern:str="", headers:dict={}, query:dict={}, body:dict=None, data:dict=None) -> dict:
    if not conn.security_token: 
        credentials = AccessKeyCredential(conn.acs_access_key_id, conn.acs_secret_access_key)
    else:
        credentials = StsTokenCredential(conn.acs_access_key_id, conn.acs_secret_access_key, conn.security_token)
    # 创建AcsClient连接,timeout设置请求超时时间(单位：ms)
    client = AcsClient(region_id=conn.region, credential=credentials, timeout=10000)
    # 创建API请求
    request = CommonRequest()
    # 产品接口信息参数
    request.set_product(popcode)
    request.set_version(version)
    request.set_action_name(api_name)
    if pattern:
        request.set_uri_pattern(pattern)
    # 云产品的Endpoint地址
    request.set_domain(conn._endpoint)
    request.set_endpoint(conn._endpoint)
    # 设置请求方式
    request.set_method(method)
    # 设置请求协议类型
    request.set_protocol_type('http')
    
    # 阿里云核心库SDK发起API请求时，可以设置四种类型参数（Path/Query/Body/Header）
    # Path参数用于对请求Request中设置的UriPattern进行变量替换
    # Query参数用于对请求Request中的URL参数进行设置（一般用于GET请求）
    # Body参数用于对请求Request中的HTTP Content进行设置（一般用于POST/PUT请求），在设置Body参数时，需要同时设置HTTP Content-Type，目前支持JSON和FORM两种格式
    # Header参数用于对请求Request中的HTTP Header进行设置
    
    # 设置Headers
    # 设置身份标识,标识调用来源,无实际作用,可随意设置,必填项
    for k, v in conn._default_headers.items():
        request.add_header(k ,v)
    for k, v in headers.items():
        request.add_header(k ,v)

    request.add_header("x-acs-caller-sdk-source", conn.user_agent)
    request.add_header("x-acs-asapi-product", popcode)
    request.add_header("x-ascm-product-name", popcode)
    request.add_header("RegionId", conn.region)
    request.set_user_agent(conn.user_agent)
    default_query = {
        "RegionId": request.get_headers()["x-acs-regionid"],
        "Department": request.get_headers()["x-acs-organizationid"],
        "OrganizationId": request.get_headers()["x-acs-organizationid"],
        "ResourceGroup": request.get_headers()["x-acs-resourcegroupid"]
    }
    if query:
        query.update(default_query)
        request.set_query_params(query)
    else:
        request.set_query_params(default_query)
    if body:
        request.set_content_type('application/x-www-form-urlencoded')
        
        request.set_body_params(body)
    if data:
        request.set_content_type('application/json')
        request.set_content(data)
    
    response = client.do_action_with_exception(request)
    
    return json.loads(response)


def ecs_connect(module):
    """ Return an ecs connection"""
    ecs_params = get_profile(module.params)
    # If we have a region specified, connect to its endpoint.
    region = module.params.get('apsarastack_region')
    if region:
        try:
            ecs = connect_to_acs(footmark.ecs, module.params, **ecs_params)
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


def dns_connect(module):
    """ Return an dns connection"""
    dns_params = get_profile(module.params)
    try:
        dns = connect_to_acs(footmark.dns, module.params, **dns_params)
    except AnsibleACSError as e:
        module.fail_json(msg=str(e))
    # Otherwise, no region so we fallback to the old connection method
    return dns

def rds_connect(module):
    """ Return an rds connection"""
    rds_params = get_profile(module.params)
    try:
        rds = connect_to_acs(footmark.rds, module.params, **rds_params)
    except AnsibleACSError as e:
        module.fail_json(msg=str(e))
    # Otherwise, no region so we fallback to the old connection method
    return rds


def slb_connect(module):
    """ Return an slb connection"""
    slb_params = get_profile(module.params)
    try:
        slb = connect_to_acs(footmark.slb, module.params, **slb_params)
    except AnsibleACSError as e:
        module.fail_json(msg=str(e))
    # Otherwise, no region so we fallback to the old connection method
    return slb


def ascm_connect(module):
    """ Return an ascm connection"""
    ascm_params = get_profile(module.params)
    try:
        ascm = connect_to_universal("ascm", module.params, **ascm_params)
    except AnsibleACSError as e:
        module.fail_json(msg=str(e))
    # Otherwise, no region so we fallback to the old connection method
    return ascm


def ossbucket_connect(module):
    """ Return an oss bucket connection"""
    oss_params = get_profile(module.params)
    del oss_params["ecs_role_name"]
    try:
        oss_bucket = connect_to_bucket(footmark.oss, module.params, **oss_params)
    except AnsibleACSError as e:
        module.fail_json(msg=str(e))
    # Otherwise, no region so we fallback to the old connection method
    return oss_bucket


def ossbucket_object_conn(module):
    """ Return an oss bucket connection"""
    oss_params = get_profile(module.params)
    del oss_params["ecs_role_name"]
    try:
        oss_bucket_object = connect_oss_object(footmark.oss.Bucket, module.params, "oss", **oss_params)
    except AnsibleACSError as e:
        module.fail_json(msg=str(e))
    # Otherwise, no region so we fallback to the old connection method
    return oss_bucket_object


def ossservice_connect(module):
    """ Return an oss service connection"""
    oss_params = get_profile(module.params)
    del oss_params["ecs_role_name"]
    try:
        oss_service = connect_to_bucket_service(footmark.oss, module.params, **oss_params)
    except AnsibleACSError as e:
        module.fail_json(msg=str(e))
    # Otherwise, no region so we fallback to the old connection method
    return oss_service

def ess_connect(module):
    """ Return an ess service connection"""
    ess_params = get_profile(module.params)
    try:
        ess = connect_to_acs(footmark.ess, module.params, **ess_params)
    except AnsibleACSError as e:
        module.fail_json(msg=str(e))
    # Otherwise, no region so we fallback to the old connection method
    return ess


def ram_connect(module):
    """ Return an ram service connection"""
    ram_params = get_profile(module.params)
    try:
        ram = connect_to_acs(footmark.ram, module.params, **ram_params)
    except AnsibleACSError as e:
        module.fail_json(msg=str(e))
    # Otherwise, no region so we fallback to the old connection method
    return ram
