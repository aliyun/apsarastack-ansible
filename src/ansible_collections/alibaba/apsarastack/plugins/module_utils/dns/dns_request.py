#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkcore.auth.credentials import StsTokenCredential

# 本文提供的API调用样例仅供参考，更多详细API调用方法可参照开发文档中的“快速入门”

credentials = AccessKeyCredential('5cPgem1vhloQrbN6', 'Uu5m7rLZ4xWUSXUbTOEooFoZTq0nJk')
# 使用 STS Token
# credentials = StsTokenCredential('<your-access-key-id>', '<your-access-key-secret>', '<your-sts-token>')
# 创建AcsClient连接,timeout设置请求超时时间(单位：ms)
client = AcsClient(region_id='cn-wulan-env212-d01', credential=credentials, timeout=10000)
# 创建API请求
request = CommonRequest()
# 产品接口信息参数
request.set_product("CloudDns")
request.set_version('2021-06-24')
request.set_action_name("AddGlobalZone")
# 云产品的Endpoint地址
request.set_domain('dns-control.pop.inter.env212.shuguang.com')
# 设置请求方式
request.set_method('POST')
# 设置请求协议类型
request.set_protocol_type('http')

# 阿里云核心库SDK发起API请求时，可以设置四种类型参数（Path/Query/Body/Header）
# Path参数用于对请求Request中设置的UriPattern进行变量替换
# Query参数用于对请求Request中的URL参数进行设置（一般用于GET请求）
# Body参数用于对请求Request中的HTTP Content进行设置（一般用于POST/PUT请求），在设置Body参数时，需要同时设置HTTP Content-Type，目前支持JSON和FORM两种格式
# Header参数用于对请求Request中的HTTP Header进行设置

# 设置Headers
# 设置身份标识,标识调用来源,无实际作用,可随意设置,必填项
request.add_header("x-acs-caller-sdk-source","<your-sdk-source>")
# 调用专有云API时，一般需要提供多个公共Header参数，包括：x-acs-regionid、x-acs-organizationid、x-acs-resourcegroupid、x-acs-instanceid。详情可参照开发指南中的“获取公共Header参数"
request.add_header("x-acs-organizationid", "99")
request.add_header("x-acs-resourcegroupid", "396")
# 接口业务参数设置
request.add_body_params("Name","zhangyantest123.dev.ali.cloud.cn.hsbc3.")
# 接口业务参数设置

request.set_content_type('application/x-www-form-urlencoded')
# 发起请求，并获取返回
response = client.do_action_with_exception(request)

# python2:  print(response)
print(str(response, encoding='utf-8'))