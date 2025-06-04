# Aliyun ApsaraStack Collection
The Ansible Aliyun ApsaraStack collection includes a variety of Ansible content to help automate the management of Aliyun ApsaraStack instances. This collection is maintained by the Aliyun ApsaraStack team.

## Python version compatibility

This collection requires Python 3.6 or greater.

## Installing this collection

You can install the Aliyun ApsaraStack collection with the Ansible Galaxy CLI:
``` shell
ansible-galaxy collection install alibaba.apsarastack
```

also you can also install it through source code:

1. create a `requirements.txt` file with the following:
   ```yaml
   collections:
     - name: https://github.com/aliyun/apsarastack-ansible.git#/src/ansible_collections/alibaba
       type: git
       branch: master
   ```
2. running the commond to install alibaba.apsarastack using `requirements.txt` file:
   ```shell
   ansible-galaxy collection install -r requirements.txt
   ```

   
> The python module dependencies are not installed by `ansible-galaxy`.  They can
be manually installed using pip:
> ```shell
> pip install -r requirements.txt
> ```
> or:
> ```shell
> pip install footmark jmespath==0.10.0
> ```


## Using this collection

You can either call modules by their Fully Qualified Collection Namespace (FQCN), such as `alibaba.apsarastack.ali_vpc`, or you can call modules by their short name if you list the `alibaba.apsarastack` collection in the playbook's `collections` keyword:

```yaml
---
- name: Using module alibaba.apsarastack.ali_vpc
  hosts: localhost
  remote_user: root

  vars:
    name: "ansible-testacc-ali_vpc-module"
    vpc_cidr: "172.16.0.0/12"
    vpc_description: "Create a new VPC resource via Ansible example apsarastack-ecs-vpc."

  tasks:
    - name: Create a new vpc with user_cidrs
      alibaba.apsarastack.ali_vpc:
        popgw_domain: "xxxx"
        region: "xxxx"
        access_key: "xxxx"
        secret_key: "xxxx"
        organization_id: "xxxx"
        resourcegroupset_id: "xxxx"
        cidr_block: '{{ vpc_cidr }}'
        vpc_name: '{{ name }}-user_cidrs'
        description: '{{ vpc_description }}'
        user_cidrs:
          - 172.16.100.0/24
          - 172.16.101.0/24
```

## plugins/modules
There are several files in the module directory, and these files describe some function that can operate apsarastack products.

- `ali_disk.py`: Create, Attach, Detach, or Delete a disk in ECS  
- `ali_disk_info.py`: Query information about a disk in ECS  
- `ali_vpc.py`: Create or Delete a VPC  
- `ali_vpc_info.py`: Query information about a VPC  
- `ali_vswitch.py`: Create or Delete a VSwitch  
- `ali_vswitch_info.py`: Query information about a VSwitch  
- `ali_dns_domain.py`: Create, Delete, or Update a DNS domain  
- `ali_dns_domain_info.py`: Query information about a DNS domain  
- `ali_ecs_tag.py`: Manage tags for ECS instances and disks (Create, Delete, Update, or Query)  
- `ali_eip.py`: Allocate or Release an Elastic IP address  
- `ali_eip_info.py`: Query information about an Elastic IP address  
- `ali_image.py`: Create or Delete a custom image  
- `ali_image_info.py`: Query information about an image  
- `ali_instance.py`: Create, Start, Stop, Restart, or Terminate an ECS instance  
- `ali_instance_info.py`: Query information about an ECS instance  
- `ali_instance_type_facts.py`: Query available ECS instance types  
- `ali_rds_account.py`: Create or Delete an RDS account  
- `ali_rds_account_info.py`: Query information about an RDS account  
- `ali_rds_backup.py`: Create or Delete an RDS backup  
- `ali_rds_backup_info.py`: Query information about an RDS backup  
- `ali_rds_database.py`: Create or Delete an RDS database  
- `ali_rds_database_info.py`: Query information about an RDS database  
- `ali_rds_instance.py`: Create or Delete an RDS instance  
- `ali_rds_instance_info.py`: Query information about an RDS instance  
- `ali_route_entry.py`: Add or Remove a route entry  
- `ali_route_entry_info.py`: Query information about a route entry  
- `ali_security_group.py`: Create or Delete a Security Group  
- `ali_security_group_info.py`: Query information about a Security Group  
- `ali_slb_lb.py`: Create or Delete a Load Balancer  
- `ali_slb_lb_info.py`: Query information about a Load Balancer  
- `ali_slb_listener.py`: Create or Delete a Load Balancer listener  
- `ali_slb_listener_info.py`: Query information about a Load Balancer listener  
- `ali_slb_server.py`: Add or Remove backend servers from a Load Balancer  
- `ali_slb_server_info.py`: Query backend servers of a Load Balancer  
- `ali_slb_tag.py`: Manage tags for a Load Balancer (Create, Delete, Update, or Query)  
- `ali_slb_vsg.py`: Create or Delete a Virtual Server Group for a Load Balancer  
- `ali_slb_vsg_info.py`: Query information about a Virtual Server Group  
- `ali_ess_instance.py`: Create or Delete an Auto Scaling instance  
- `ali_ess_configuration.py`: Create or Delete an Auto Scaling configuration  
- `ali_ess_group.py`: Create or Delete an Auto Scaling group  
- `ali_ess_rule.py`: Create or Delete an Auto Scaling rule  
- `ali_ess_task.py`: Query or Manage Auto Scaling tasks  
- `ali_ram_group.py`: Create or Delete a RAM group  
- `ali_ram_group_info.py`: Query information about a RAM group  
- `ali_ram_login_profile_info.py`: Query login profile details for a RAM user  
- `ali_ram_login_profile.py`: Create or Delete a RAM login profile  
- `ali_ram_policy_info.py`: Query information about a RAM policy  
- `ali_ram_policy.py`: Create or Delete a RAM policy  
- `ali_ram_role_info.py`: Query information about a RAM role  
- `ali_ram_role.py`: Create or Delete a RAM role  
- `ali_ram_user_info.py`: Query information about a RAM user  
- `ali_ram_user.py`: Create or Delete a RAM user  
- `ali_oss_bucket_info.py`: Query information about an OSS bucket  
- `ali_oss_bucket.py`: Create or Delete an OSS bucket  
- `ali_oss_object_info.py`: Query information about an OSS object  
- `ali_oss_object.py`: Upload, Delete, or Manage an OSS object  

## lib/ansible/module_utils
In the module utils directory, the file apsarastack_ecs.py identifies and gains playbook params, and provides this params to modules/*.py. In addition, this file implements connection between ansible and Apsarastack API via footmark.

## examples
There are some playbooks to create some apsarastack resource or build infrastructure architecture.

### Execute playbook

* Input your apsarastack access key in the playbook or set environment variable:`APSARASTACK_ACCESS_KEY` and `APSARASTACK_SECRET_KEY`).
* Input others resource params in the playbook.
* execute ansible-playbook command as follows:

	  $ ansible-playbook xxx.yml
	   
## Refrence

Ansible Document: https://docs.ansible.com/ansible/latest/

Ansible Apsarastack: [Docs Details](http://47.88.222.42:8080/ansible-apsarastack/latest/modules/list_of_cloud_modules.html)
