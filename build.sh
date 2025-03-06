#!/bin/bash

ansible-galaxy collection build  src/ansible_collections/alibaba/apsarastack/ --output-path dist $*