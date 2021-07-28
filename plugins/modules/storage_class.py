#!/usr/bin/python

# Copyright: (c) 2021, Mihael Trajbarič <mihael.trajbaric@xlab.si>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: storage_class

short_description: Creates k8s StorageClass

version_added: "1.0.0"

description: Creates k8s PersistentVolumeClaim, which describes the parameters for a class of storage for which
             PersistentVolumes can be dynamically provisioned. StorageClasses are non-namespaced and immutable, once
             created they cannot be patched.

extends_documentation_fragment:
    - sodalite.k8s.common_options
    - sodalite.k8s.metadata_options
    - kubernetes.core.k8s_auth_options
    - kubernetes.core.k8s_wait_options
    - kubernetes.core.k8s_delete_options

options:
    provisioner:
        description:
        - Indicates the type of the provisioner.
        type: str
        required: true
    allow_volume_expansion:
        description:
        - Shows whether the storage class allow volume to expand.
        type: bool
    allowed_topologies:
        description:
        - Restrict the node topologies where volumes can be dynamically provisioned.
        - The requirements are ANDed.
        - Each volume plugin defines its own supported topology specifications.
        - An empty I(allowed_topologies) list means there is no topology restriction.
        - This field is only honored by servers that enable the VolumeScheduling feature.
        - This is an alpha feature and may change in the future.
        type: list
        elements: dict
        suboptions:
            key:
                description:
                - The label key that the selector applies to.
                type: str
                required: true
            values:
                description:
                - An array of string values.
                - One value must match the label to be selected.
                - Each entry in Values is ORed.
                type: list
                elements: str
                required: true
    mount_options:
        description:
        - mountOptions for dynamically provisioned PersistentVolumes of this storage class.
        - Not validated - mount of the PVs will simply fail if one is invalid.
        type: list
        elements: str
    parameters:
        description:
        - Holds the parameters for the provisioner that should create volumes of this storage class.
        type: dict
    reclaim_policy:
        description:
        - What happens to dynamically provisioned PersistentVolumes of this storage class when released from its claim.
        type: str
        default: Delete
        choices: [ Retain, Delete, Recycle ]
    volume_binding_mode:
        description:
        - Controls when volume binding and dynamic provisioning should occur.
        - The I(volume_binding_mode = 'Immediate') mode indicates that volume binding and dynamic provisioning occurs
          once the PersistentVolumeClaim is created. For storage backends that are topology-constrained and not globally
          accessible from all Nodes in the cluster, PersistentVolumes will be bound or provisioned without knowledge of
          the Pod's scheduling requirements. This may result in unschedulable Pods.
        - A cluster administrator can address this issue by specifying the
          I(volume_binding_mode = 'WaitForFirstConsumer') mode which will delay the binding and provisioning of a
          PersistentVolume until a Pod using the PersistentVolumeClaim is created. PersistentVolumes will be selected
          or provisioned conforming to the topology that is specified by the Pod's scheduling constraints. These
          include, but are not limited to, resource requirements, node selectors, pod affinity and anti-affinity,
          and taints and tolerations.
        - This field is only honored by servers that enable the VolumeScheduling feature.
        - More info U(https://kubernetes.io/docs/concepts/storage/storage-classes/#volume-binding-mode)
        type: str
        default: Immediate
        choices: [ Immediate, WaitForFirstConsumer ]

seealso:
- name: K8s StorageClass documentation
  description: Complete storage class documentation on kubernetes website
  link: https://kubernetes.io/docs/concepts/storage/storage-classes/


author:
    - Mihael Trajbarič (@mihaTrajbaric)
'''

# TODO
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
        "apiVersion": "storage.k8s.io/v1",
        "kind": "StorageClass",
        "metadata": {
            "name": params.get('name'),
            "labels": params.get('labels'),
            "annotations": params.get('annotations')
        },
        'provisioner': params.get('provisioner'),
        'allowVolumeExpansion': params.get('allow_volume_expansion'),
        'allowedTopologies': [
            {
                'matchLabelExpressions': params.get('allowed_topologies')
            }
        ],
        'mountOptions': params.get('mount_options'),
        'parameters': params.get('parameters'),
        'reclaimPolicy': params.get('reclaim_policy'),
        'volumeBindingMode': params.get('volume_binding_mode')
    }
    return clean_dict(body)


def validate(module, k8s_definition):
    CommonValidation.metadata(module, k8s_definition)

    parameters = k8s_definition.get('parameters', dict())
    if not Validators.string_string_dict(parameters):
        module.fail_json(msg="parameters should be map[string]string")


def main():
    # TODO no namespace!!!
    argspec = common_arg_spec()
    argspec.update(dict(
        provisioner=dict(type='str', required=True),
        allow_volume_expansion=dict(type='bool'),
        allowed_topologies=dict(type='list', elements='dict', options=dict(
            key=dict(type='str', required=True, no_log=False),
            values=dict(type='list', elements='str', required=True)
        )),
        mount_options=dict(type='list', elements='str'),
        parameters=dict(type='dict'),
        reclaim_policy=dict(type='str', choices=['Retain', 'Delete', 'Recycle'], default='Delete'),
        volume_binding_mode=dict(type='str', choices=['Immediate', 'WaitForFirstConsumer'], default='Immediate'),
    ))
    # required_if = [
    #     ('state', 'present', ('provisioner',))
    # ]

    module = AnsibleModule(argument_spec=argspec,
                           # required_if=required_if,
                           supports_check_mode=True)
    from ansible_collections.sodalite.k8s.plugins.module_utils.k8s_connector import execute_module

    k8s_def = definition(module.params)
    if module.params.get('state') != 'absent':
        validate(module, k8s_def)

    execute_module(module, k8s_def)


if __name__ == '__main__':
    main()
