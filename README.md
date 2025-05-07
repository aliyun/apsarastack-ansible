# Aliyun ApsaraStack Collection
The Ansible Aliyun ApsaraStack collection includes a variety of Ansible content to help automate the management of Aliyun ApsaraStack instances. This collection is maintained by the Aliyun ApsaraStack team.

## Python version compatibility

This collection requires Python 3.6 or greater.

## Installing this collection

You can install the Aliyun ApsaraStack collection with the Ansible Galaxy CLI:

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

- `ali_instance.py`: Create, Start, Stop, Restart or Terminate an Instance in ECS. Add or Remove Instance to/from a Security Group
- `ali_disk.py`: Create, Attach, Detach or Delete a disk in ECS
- `ali_security_group.py`: Create or Delete a Security Group
- `ali_vpc.py`: Create or Delete a Vpc.
- `ali_vswitch.py`: Create or Delete a VSwitch.
- `ali_route_entry.py`: Create or Delete a route entry.
- `ali_slb_lb.py`: Create or Delete a Load balancer.
- `ali_slb_listener.py`: Create or Delete a listener for one Load balancer.
- `ali_slb_server.py`: Add or Remove backend server to/from Load balancer.

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
