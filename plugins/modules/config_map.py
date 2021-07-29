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

description: Creates k8s ConfigMap which holds configuration data for pods to consume.

extends_documentation_fragment:
    - sodalite.k8s.common_update_options
    - sodalite.k8s.metadata_options
    - kubernetes.core.k8s_auth_options
    - kubernetes.core.k8s_wait_options
    - kubernetes.core.k8s_delete_options

options:
    data:
        description:
            - Contains the configuration data.
            - Each key must consist of alphanumeric characters, '-', '_' or '.'.
            - Values with non-UTF-8 byte sequences must use the C(binary_data) field.
            - The keys stored in C(data) must not overlap with the keys in the C(binary_data) field, this is enforced
              during validation process.
        type: dict
    binary_data:
        description:
           - Contains the binary data.
           - Each key must consist of alphanumeric characters, '-', '_' or '.'.
           - Can contain byte sequences that are not in the UTF-8 range.
           - The keys stored in C(binary_data) must not overlap with the ones in the C(data) field, this is enforced
             during validation process.
        type: dict
    immutable:
        description:
            - If set to C(true), ensures that data stored in the ConfigMap cannot be updated (only object metadata
              can be modified).
            - If set to C(false), the field can be modified at any time.
        type: bool
        default: false

author:
    - Mihael Trajbarič (@mihaTrajbaric)
'''
EXAMPLES = r'''
# Create new configmap
- name: Config for xOpera rest api
  sodalite.k8s.config_map:
    name: xOpera-config
    data:
      db_ip: postgres-service
# Replace config
- name: Config for xOpera rest api
  sodalite.k8s.config_map:
    name: xOpera-config
    state: present
    force: yes
    data:
      db_ip: mysql-service
# Create config with binary data
- name: Binary config
  sodalite.k8s.config_map:
    name: binary-config
    binary_data:
      db_ip: cG9zdGdyZXMtc2VydmljZQ==
# Create config with metadata
- name: Labels and annotations
  sodalite.k8s.config_map:
    name: xOpera-config
    labels:
      app: postgres
    annotations:
      type: my_config
    data:
      db_ip: postgres-service
# Remove config
- name: Config for xOpera rest api
  sodalite.k8s.config_map:
    name: xOpera-config
    state: absent
    data:
      db_ip: postgres-service
'''

RETURN = r'''
result:
  description:
  - The created, patched, or otherwise present object. Will be empty in the case of a deletion.
  returned: success
  type: complex
  contains:
     api_version:
       description: The versioned schema of this representation of an object.
       returned: success
       type: str
     kind:
       description: Represents the REST resource this object represents.
       returned: success
       type: str
     metadata:
       description: Standard object metadata. Includes name, namespace, annotations, labels, etc.
       returned: success
       type: dict
     spec:
       description: Specific attributes of the object.
       returned: success
       type: dict
     status:
       description: Current status details for the object.
       returned: success
       type: dict
     duration:
       description: elapsed time of task in seconds
       returned: when C(wait) is true
       type: int
       sample: 48
     error:
       description: error while trying to create/delete the object.
       returned: error
       type: dict
'''

from ansible_collections.sodalite.k8s.plugins.module_utils.ansiblemodule import AnsibleModule
from ansible_collections.sodalite.k8s.plugins.module_utils.args_common import (update_arg_spec,
                                                                               UPDATE_MUTUALLY_EXCLUSIVE)
from ansible_collections.sodalite.k8s.plugins.module_utils.common import Validators, CommonValidation
from ansible_collections.sodalite.k8s.plugins.module_utils.helper import clean_dict


def definition(params):

    body = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {
            "name": params.get('name'),
            "labels": params.get('labels'),
            "annotations": params.get('annotations')
        },
        "immutable": params.get('immutable'),
        "binaryData": params.get('binary_data'),
        "data": params.get('data')
    }

    return clean_dict(body)


def validate(module, k8s_definition):

    CommonValidation.metadata(module, k8s_definition)

    if not Validators.dns_subdomain(k8s_definition['metadata']['name']):
        module.fail_json(msg=f"'name' {Validators.dns_subdomain_msg}")

    data = k8s_definition.get('data', dict())
    binary_data = k8s_definition.get('binaryData', dict())

    data_keys_valid = all([Validators.alnum_ext(key) for key in data.keys()])
    binary_data_keys_valid = all([Validators.alnum_ext(key) for key in binary_data.keys()])
    keys_unique = len(set(list(data.keys()) + list(binary_data.keys()))) == len(data.keys()) + len(binary_data.keys())

    if not data_keys_valid:
        module.fail_json(msg="Keys in data must consist of alphanumeric characters, '-', '_' or '.'")
    if not binary_data_keys_valid:
        module.fail_json(msg="Keys in binary_data must consist of alphanumeric characters, '-', '_' or '.'")
    if not keys_unique:
        module.fail_json(msg="Keys in data and binary_data should not overlap")
    if not Validators.string_byte_dict(binary_data):
        module.fail_json(msg="binary_data should be map[string][]byte")


def main():
    argspec = update_arg_spec()
    argspec.update(dict(
        data=dict(type='dict'),
        binary_data=dict(type='dict'),
        immutable=dict(type='bool', default=False)
    ))

    module = AnsibleModule(argument_spec=argspec, mutually_exclusive=UPDATE_MUTUALLY_EXCLUSIVE, supports_check_mode=True)
    from ansible_collections.sodalite.k8s.plugins.module_utils.k8s_connector import execute_module

    k8s_def = definition(module.params)
    if module.params.get('state') != 'absent':
        validate(module, k8s_def)

    execute_module(module, k8s_def)


if __name__ == '__main__':
    main()
