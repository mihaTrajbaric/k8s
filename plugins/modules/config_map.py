#!/usr/bin/python

# Copyright: (c) 2021, Mihael Trajbarič <mihael.trajbaric@xlab.si>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: config_map

short_description: Creates k8s ConfigMap

version_added: "1.0.0"

description: Creates k8s ConfigMap which can be used to configure deployments, StatefullSets etc.

options:
    name:
        description: Name fo ConfigMap.
        required: true
        type: str
    state:
        description:
          - The ConfigMap state
        default: present
        choices: [ "present", "absent"]
        type: str
    data:
        description:
            - Dictionary of key,value pairs.
        type: dict

        

author:
    - Mihael Trajbarič (@mihaTrajbaric)
'''
# TODO fix
EXAMPLES = r'''
# Pass in a message
- name: Test with a message
  my_namespace.my_collection.my_test_info:
    name: hello world
'''

# TODO fix
RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original name param that was passed in.
    type: str
    returned: always
    sample: 'hello world'
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'goodbye'
my_useful_info:
    description: The dictionary containing information about your system.
    type: dict
    returned: always
    sample: {
        'foo': 'bar',
        'answer': 42,
    }
'''

import copy

from ansible_collections.sodalite.k8s.plugins.module_utils.ansiblemodule import AnsibleModule
from ansible_collections.sodalite.k8s.plugins.module_utils.args_common import (COMMON_ARG_SPEC)


def argspec():
    argument_spec = copy.deepcopy(COMMON_ARG_SPEC)
    argument_spec['data'] = dict(type='dict')

    return argument_spec


def main():
    mutually_exclusive = [
        ('force', 'apply')
    ]
    module = AnsibleModule(argument_spec=argspec(), mutually_exclusive=mutually_exclusive, supports_check_mode=True)
    from ansible_collections.sodalite.k8s.plugins.module_utils.common import (
        K8s)
    # TODO add additional options
    body = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {
            "name": module.params.get('name')
        },
        "data": module.params.get('data')
    }
    k8s = K8s(module, body)
    k8s.execute_module()


if __name__ == '__main__':
    main()
