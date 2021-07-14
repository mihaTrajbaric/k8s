#!/usr/bin/python

# Copyright: (c) 2021, Mihael Trajbarič <mihael.trajbaric@xlab.si>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: pvc

short_description: Creates k8s PersistentVolumeClaim

version_added: "1.0.0"

description: Creates k8s PersistentVolumeClaim, which is a user's request for and claim to a persistent volume

extends_documentation_fragment:
    - sodalite.k8s.common_options
    - sodalite.k8s.metadata_options
    - kubernetes.core.k8s_auth_options
    - kubernetes.core.k8s_wait_options
    - kubernetes.core.k8s_delete_options

options:
    access_modes:
        description:
        - Contains the desired access modes the volume should have.
        - Possible list elements are C(ReadWriteOnce), C(ReadOnlyMany), C(ReadWriteMany)
        - If I(state=present), at least 1 access_mode should be specified.
        type: list
        elements: str
    selector:
        description:
        - A label query over a set of resources.
        - The result of C(match_labels) and C(match_expressions) are ANDed.
        - An empty label selector matches all objects.
        - A null label selector matches no objects.
        type: dict
        suboptions:
            match_labels:
                description:
                - A map of {C(key),C(value)} pairs.
                - A single {C(key),C(value)} in the I(match_labels) map is equivalent to an element of
                  I(match_expressions), whose key field is C(key), the operator is C(In), and the values array contains
                  only C(value).
                - The requirements are ANDed.
                type: dict
            match_expressions:
                description:
                - A list of label selector requirements.
                - The requirements are ANDed.
                - A label selector requirement is a selector that contains values, a key, and an operator that relates
                  the key and values.
                type: list
                elements: dict
                suboptions:
                    key:
                        description:
                        - The label key that the selector applies to.
                        - Patch strategy is merge on I(key=key)
                        type: str
                        required: yes
                    operator:
                        description:
                        - Represents a key's relationship to a set of values.
                        type: str
                        choices: [In, NotIn, Exists, DoesNotExist]
                        required: yes
                    values:
                        description:
                        - An array of string values.
                        - If the I(operator=In) or I(operator=NotIn), the values array must be non-empty.
                        - If the I(operator=Exists) or I(operator=DoesNotExist), the values array must be empty.
                        - This array is replaced during a strategic merge patch.
                        type: list
                        elements: str
    storage_request:
        description:
        - Describes the minimum amount of compute resources required.
        - Required when I(state=present)
        type: str
    storage_limit:
        description:
        - Describe the maximum amount of compute resources allowed.
        type: str
    volume_name:
        description:
        - The binding reference to the PersistentVolume backing this claim.
        type: str
    storage_class_name:
        description:
        - Name of the StorageClass required by the claim.
        - When both I(selector) and I(storage_class_name) are specified together, the requirements are C(ANDed)
          together.
        type: str
    volume_mode:
        description:
        - Defines what type of volume is required by the claim.
        - A volume with I(volume_mode=Filesystem) is mounted into Pods into a directory. If the volume is backed by a
          block device and the device is empty, Kubernetes creates a filesystem on the device before mounting it for
          the first time.
        - A volume with I(volume_mode=Block)is used as a raw block device. Such volume is presented into a Pod as a
          block device, without any filesystem on it. This mode is useful to provide a Pod the fastest possible way to
          access a volume, without any filesystem layer between the Pod and the volume. On the other hand, the
          application running in the Pod must know how to handle a raw block device.
        type: str
        choices: [Filesystem, Block]
        default: Filesystem


author:
    - Mihael Trajbarič (@mihaTrajbaric)
'''

EXAMPLES = r'''
# Create PersistentVolumeClaim
- name: Create simple PersistentVolumeClaim
  sodalite.k8s.pvc:
    name: pvc-test
    state: present
    access_modes:
        - ReadWriteMany
        - ReadWriteOnce
    storage_request: 5Gi

# Create PersistentVolumeClaim with match_expressions
- name: PersistentVolumeClaim with matchExpressions selector
  sodalite.k8s.pvc:
    name: pvc-test
    state: present
    selector:
        match_expressions:
          - key: app-volume
            operator: In
            values: [postgres, mysql]
    access_modes:
        - ReadWriteMany
        - ReadWriteOnce
    storage_request: 5Gi

# Create PersistentVolumeClaim with match_labels
- name: PersistentVolumeClaim with matchLabels selector
  sodalite.k8s.pvc:
    name: pvc-test
    state: present
    selector:
        match_labels:
          app-volume: postgres
    access_modes:
        - ReadWriteMany
        - ReadWriteOnce
    storage_request: 5Gi

# Create PersistentVolumeClaim with ResourceRequirements
- name: PersistentVolumeClaim with storage_request and storage_limit
  sodalite.k8s.pvc:
    name: pvc-test
    state: present
    access_modes:
        - ReadWriteMany
        - ReadWriteOnce
    storage_request: 5Gi
    storage_limit: 10Gi

# Remove PersistentVolumeClaim
- name: Remove pvc
  sodalite.k8s.pvc:
    name: pvc-test
    state: absent
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
from ansible_collections.sodalite.k8s.plugins.module_utils.args_common import common_arg_spec
from ansible_collections.sodalite.k8s.plugins.module_utils.common import Validators, CommonValidation
from ansible_collections.sodalite.k8s.plugins.module_utils.helper import clean_dict


def definition(params):

    body = {
        "apiVersion": "v1",
        "kind": "PersistentVolumeClaim",
        "metadata": {
            "name": params.get('name'),
            "labels": params.get('labels'),
            "annotations": params.get('annotations')
        },
        'spec': {
            'accessModes': params.get('access_modes'),
            'selector': {
                'matchExpressions': (params.get('selector') or {}).get('match_expressions'),
                'matchLabels': (params.get('selector') or {}).get('match_labels')
            },
            'resources': {
                'requests': {
                    'storage': params.get('storage_request')
                },
                'limits': {
                    'storage': params.get('storage_limit')
                }
            },
            'volumeName': params.get('volume_name'),
            'storageClassName': params.get('storage_class_name'),
            'volumeMode': params.get('volume_mode')
        }
    }
    return clean_dict(body)


def validate(module, k8s_definition):
    CommonValidation.metadata(module, k8s_definition)

    if not Validators.dns_subdomain(k8s_definition['metadata']['name']):
        module.fail_json(msg="'name' should be a valid lowercase RFC 1123 subdomain. It must consist of lower case "
                             "alphanumeric characters, '-' or '.', and must start and end with an "
                             "alphanumeric character")

    spec_keys = list(k8s_definition['spec'].keys())

    access_modes = k8s_definition['spec'].get('accessModes', list())
    if not access_modes:
        module.fail_json(msg="Access_modes should have at least 1 element")

    access_modes_valid = all([item in ('ReadWriteOnce', 'ReadOnlyMany', 'ReadWriteMany') for item in access_modes])
    if not access_modes_valid:
        module.fail_json(msg="Elements of access_modes should be chosen from "
                             "('ReadWriteOnce', 'ReadOnlyMany', 'ReadWriteMany')")

    if 'selector' in spec_keys:
        match_expressions = k8s_definition['spec']['selector'].get('matchExpressions', list())
        for expression in match_expressions:
            valid_keys = ('In', 'NotIn', 'Exists', 'DoesNotExist')
            operator = expression.get('operator')
            if operator not in valid_keys:
                module.fail_json(msg="Every selector.match_expressions.key should be chosen "
                                     "from {0}".format({', '.join(valid_keys)}))
            values_condition = (operator in ('In', 'NotIn')) == bool(expression.get('values'))
            if not values_condition:
                module.fail_json(msg="If in any selector.match_expressions operator is 'In' or 'NotIn', the values "
                                     "array must be non-empty. If operator is 'Exists' or 'DoesNotExist', the values "
                                     "array must be empty.")
        match_labels = k8s_definition['spec']['selector'].get('matchLabels', dict())
        if not Validators.string_string_dict(match_labels):
            module.fail_json(msg="Selector.match_labels should be map[string]string")

    if 'resources' in spec_keys:
        limits = k8s_definition['spec']['resources'].get('limits', dict())
        if not Validators.string_quantity_dict(limits):
            module.fail_json(msg="Storage_limit should be map[string]Quantity")

        requests = k8s_definition['spec']['resources'].get('requests', dict())
        if not Validators.string_quantity_dict(requests):
            module.fail_json(msg="Storage_request should be map[string]Quantity")


def main():
    argspec = common_arg_spec()
    argspec.update(dict(
        access_modes=dict(type='list', elements='str'),
        selector=dict(type='dict', options=dict(
            match_labels=dict(type='dict'),
            match_expressions=dict(type='list', elements='dict', options=dict(
                key=dict(type='str', required=True, no_log=False),
                operator=dict(type='str', required=True, choices=['In', 'NotIn', 'Exists', 'DoesNotExist']),
                values=dict(type='list', elements='str')
            ))
        )),
        storage_request=dict(type='str'),
        storage_limit=dict(type='str'),
        volume_name=dict(type='str'),
        storage_class_name=dict(type='str'),
        volume_mode=dict(type='str', choices=['Filesystem', 'Block'], default='Filesystem')
    ))
    required_if = [
        ('state', 'present', ('access_modes', 'storage_request'))
    ]

    module = AnsibleModule(argument_spec=argspec,
                           required_if=required_if,
                           supports_check_mode=True)
    from ansible_collections.sodalite.k8s.plugins.module_utils.k8s_connector import execute_module

    volume_claim_def = definition(module.params)
    if module.params.get('state') != 'absent':
        validate(module, volume_claim_def)

    execute_module(module, volume_claim_def)


if __name__ == '__main__':
    main()
