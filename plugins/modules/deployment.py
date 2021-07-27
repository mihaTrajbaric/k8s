#!/usr/bin/python

# Copyright: (c) 2021, Mihael Trajbarič <mihael.trajbaric@xlab.si>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: deployment

short_description: Creates k8s Deployment

version_added: "1.0.0"

description: Creates k8s Deployment, provides declarative updates for Pods and ReplicaSets. You can define Deployments
             to create new ReplicaSets, or to remove existing Deployments and adopt all their resources with new
             Deployments.

extends_documentation_fragment:
    - sodalite.k8s.common_update_options
    - sodalite.k8s.selector_options
    - sodalite.k8s.metadata_options
    - kubernetes.core.k8s_auth_options
    - kubernetes.core.k8s_wait_options
    - kubernetes.core.k8s_delete_options

options:
    containers:
        description:
        - List of containers belonging to the pod.
        - There must be at least one container in a Pod.
        type: list
        elements: dict
        suboptions:
            name:
                description:
                - Name of the container specified as a DNS_LABEL.
                - Each container in a pod must have a unique name (DNS_LABEL).
                - Cannot be updated.
                type: str
                required: true
            image:
                description:
                - Docker image name.
                -  This field is optional to allow higher level config management to default or override
                   container images.
                - More info U(https://kubernetes.io/docs/concepts/containers/images)
                type: str
            image_pull_policy:
                description:
                - Image pull policy.
                - Defaults to Always if :latest tag is specified, or IfNotPresent otherwise.
                - Cannot be updated.
                - More info U(https://kubernetes.io/docs/concepts/containers/images#updating-images)
                type: str
                choices: [ Always, Never, IfNotPresent ]
            command:
                description:
                - Entrypoint array.
                - Not executed within a shell.
                - The docker image's ENTRYPOINT is used if this is not provided.
                - Variable references $(VAR_NAME) are expanded using the container's environment.
                - If a variable cannot be resolved, the reference in the input string will be unchanged.
                - The $(VAR_NAME) syntax can be escaped with a double $$, ie $$(VAR_NAME).
                - Escaped references will never be expanded, regardless of whether the variable exists or not.
                - Cannot be updated.
                - More info U(https://kubernetes.io/docs/tasks/inject-data-application/define-command-argument-container/#running-a-command-in-a-shell)
                type: list
                elements: str
            args:
                description:
                - Arguments to the entrypoint.
                - The docker image's CMD is used if this is not provided.
                - Variable references $(VAR_NAME) are expanded using the container's environment.
                - If a variable cannot be resolved, the reference in the input string will be unchanged.
                - The $(VAR_NAME) syntax can be escaped with a double $$, ie $$(VAR_NAME).
                - Escaped references will never be expanded, regardless of whether the variable exists or not.
                - Cannot be updated.
                - More info U(https://kubernetes.io/docs/tasks/inject-data-application/define-command-argument-container/#running-a-command-in-a-shell)
                type: list
                elements: str
            working_dir:
                description:
                - Container's working directory.
                - If not specified, the container runtime's default will be used, which might be configured in the
                  container image.
                - Cannot be updated.
                type: str
                aliases: [ workdir ]
            ports:
                description:
                - List of ports to expose from the container.
                - Exposing a port here gives the system additional information about the network connections a
                  container uses, but is primarily informational.
                - Not specifying a port here DOES NOT prevent that port from being exposed.
                - Any port which is listening on the default "0.0.0.0" address inside a container will be accessible
                  from the network.
                - Cannot be updated.
                type: list
                elements: dict
                suboptions:
                    container_port:
                        description:
                        - Number of port to expose on the pod's IP address.
                        - This must be a valid port number, 0 < x < 65536.
                        type: int
                        required: true
                    host_ip:
                        description:
                        - What host IP to bind the external port to.
                        type: str
                    host_port:
                        description:
                        - Number of port to expose on the host.
                        - If specified, this must be a valid port number, 0 < x < 65536.
                        type: int
                    name:
                        description:
                        - If specified, this must be an IANA_SVC_NAME and unique within the pod.
                        - Each named port in a pod must have a unique name.
                        - Name for the port that can be referred to by services.
                        type: str
                    protocol:
                        description:
                        - Protocol for port.
                        type: str
                        default: TCP
                        choices: [ UDP, TCP, SCTP ]
            env:
                description:
                - List of environment variables to set in the container.
                - Cannot be updated.
                type: list
                elements: dict
                suboptions:
                    name:
                        description:
                        - Name of the environment variable.
                        - Must be a C_IDENTIFIER.
                        type: str
                        required: true
                    value:
                        description:
                        - Variable references $(VAR_NAME) are expanded using the previous defined environment variables
                          in the container and any service environment variables.
                        - If a variable cannot be resolved, the reference in the input string will be unchanged.
                        - The $(VAR_NAME) syntax can be escaped with a double $$, ie $$(VAR_NAME).
                        - Escaped references will never be expanded, regardless of whether the variable exists or not.
                        type: str
                    config_map:
                        description:
                        - Selects a key of a ConfigMap.
                        type: dict
                        suboptions:
                            key:
                                description:
                                - The key to select.
                                type: str
                                required: true
                            name:
                                description:
                                - Name of the referent.
                                - More info U(https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#names)
                                type: str
                            optional:
                                description:
                                - Specify whether the ConfigMap or its key must be defined.
                                type: bool
                    secret:
                        description:
                        - Selects a key of a secret in the pod's namespace.
                        type: dict
                        suboptions:
                            key:
                                description:
                                - The key of the secret to select from.
                                - Must be a valid secret key.
                                type: str
                                required: true
                            name:
                                description:
                                - Name of the referent.
                                - More info U(https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#names)
                                type: str
                            optional:
                                description:
                                - Specify whether the Secret or its key must be defined.
                                type: bool
            env_from:
                description:
                - List of sources to populate environment variables in the container.
                - The keys defined within a source must be a C_IDENTIFIER.
                - All invalid keys will be reported as an event when the container is starting.
                - When a key exists in multiple sources, the value associated with the last source will take precedence.
                - Values defined by an Env with a duplicate key will take precedence.
                - Cannot be updated.
                type: list
                elements: dict
                suboptions:
                    config_map:
                        description:
                        - The ConfigMap to select from.
                        - The contents of the target ConfigMap's Data field will represent the key-value pairs as
                          environment variables.
                        type: dict
                        suboptions:
                            name:
                                description:
                                - Name of the referent.
                                - More info U(https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#names)
                                type: str
                            optional:
                                description:
                                - Specify whether the ConfigMap must be defined.
                                type: bool
                    prefix:
                        description:
                        - An optional identifier to prepend to each key in the ConfigMap.
                        - Must be a C_IDENTIFIER.
                        type: str
                    secret:
                        description:
                        - The Secret to select from.
                        - The contents of the target Secret's Data field will represent the key-value pairs as
                          environment variables.
                        type: dict
                        suboptions:
                            name:
                                description:
                                - Name of the referent.
                                - More info U(https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#names)
                                type: str
                            optional:
                                description:
                                - Specify whether the Secret must be defined.
                                type: bool
            volume_mounts:
                description:
                - Pod volumes to mount into the container's filesystem.
                - Each VolumeMount describes a mounting of a Volume within a container.
                - Cannot be updated.
                type: list
                elements: dict
                suboptions:
                    path:
                        description:
                        - Path within the container at which the volume should be mounted.
                        - Must not contain ':'.
                        type: str
                        required: true
                    name:
                        description:
                        - This must match the Name of a Volume.
                        type: str
                        required: true
                    propagation:
                        description:
                        - determines how mounts are propagated from the host to container and the other way around.
                        - More info U(https://kubernetes.io/docs/concepts/storage/volumes/#mount-propagation)
                        type: str
                        default: "None"
                        choices: [None, HostToContainer, Bidirectional]
                    read_only:
                        description:
                        - Mounted read-only if true, read-write otherwise (false or unspecified).
                        type: bool
                        default: false
                    sub_path:
                        description:
                        - Path within the volume from which the container's volume should be mounted.
                        - "\"\" means volume's root."
                        type: str
                        default: "\"\""
                    sub_path_expr:
                        description:
                        - Expanded path within the volume from which the container's volume should be mounted.
                        - Behaves similarly to I(sub_path) but environment variable references $(VAR_NAME) are expanded
                          using the container's environment.
                        - "\"\" means volume's root."
                        - I(sub_path_expr) and I(sub_path) are mutually exclusive.
                        type: str
                        default: "\"\""
            volume_devices:
                description:
                - The list of block devices to be used by the container.
                - Each element describes a mapping of a raw block device within a container.
                type: list
                elements: dict
                suboptions:
                    path:
                        description:
                        - Path inside of the container that the device will be mapped to.
                        type: str
                        required: true
                    name:
                        description:
                        - I(name) must match the name of a persistentVolumeClaim (pvc) in the pod.
                        type: str
                        required: true
            resource_limits:
                description:
                - Limits describes the maximum amount of compute resources allowed.
                - More info U(https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
                type: dict
                suboptions:
                    cpu:
                        description:
                        - Maximum CPU resources.
                        - Must be in cpu units;
                        - More info U(https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#meaning-of-cpu)
                        type: str
                    memory:
                        description:
                        - Maximum memory resources.
                        - Must be in memory units;
                        - More info U(https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#meaning-of-memory)
                        type: str
            resource_requests:
                description:
                - Requests describes the minimum amount of compute resources required.
                - If I(resource_requests) is omitted for a container, it defaults to I(resource_limits) if that is
                  explicitly specified, otherwise to an implementation-defined value.
                - More info U(https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
                type: dict
                suboptions:
                    cpu:
                        description:
                        - Requested CPU resources.
                        - Must be in cpu units;
                        - More info U(https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#meaning-of-cpu)
                        type: str
                    memory:
                        description:
                        - Requested memory resources.
                        - Must be in memory units;
                        - More info U(https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#meaning-of-memory)
                        type: str
    image_pull_secrets:
        description:
        - Optional list of references to secrets in the same namespace to use for pulling any of the images used by
          this C(deployment).
        - If specified, these secrets will be passed to individual puller implementations for them to use.
        - For example, in the case of docker, only C(DockerConfig) type secrets are honored.
        - More info U(https://kubernetes.io/docs/concepts/containers/images#specifying-imagepullsecrets-on-a-pod)
        type: list
        elements: str
    enable_service_links:
        description:
        - Indicates whether information about services should be injected into pod's environment variables, matching
          the syntax of Docker links.
        type: bool
        default: true
    volumes:
        description:
        - List of volumes that can be mounted by containers belonging to the pod.
        - More info U(https://kubernetes.io/docs/concepts/storage/volumes)
        type: list
        elements: dict
        suboptions:
            name:
                description:
                - Volume's name. Must be a C(DNS_LABEL) and unique within the pod.
                - More info U(https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#names)
                type: str
                required: true
            pvc:
                description:
                - A reference to a PersistentVolumeClaim (PVC) in the same namespace.
                - This volume finds the bound PV and mounts that volume for the pod.
                - It is, essentially, a wrapper around another type of volume that is owned by someone else
                  (the system).
                - More info U(https://kubernetes.io/docs/concepts/storage/persistent-volumes#persistentvolumeclaims)
                type: dict
                suboptions:
                    claim_name:
                        description:
                        - Name of a pvc in the same namespace as the pod using this volume.
                        - More info U(https://kubernetes.io/docs/concepts/storage/persistent-volumes#persistentvolumeclaims)
                        type: str
                        required: true
                    read_only:
                        description:
                        - Will force the C(ReadOnly) setting in I(VolumeMounts).
                        type: bool
                        default: false
            config_map:
                description:
                - Adapts a ConfigMap into a volume.
                - The contents of the target ConfigMap's Data field will be presented in a volume as files using the
                  keys in the C(Data) field as the file names, unless the items element is populated with specific
                  mappings of keys to paths.
                - ConfigMap volumes support ownership management and SELinux relabeling.
                type: dict
                suboptions:
                    name:
                        description:
                        - Name of the referent.
                        - More info U(https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#names)
                        type: str
                    optional:
                        description:
                        - Specify whether the ConfigMap or its keys must be defined.
                        type: bool
                    default_mode:
                        description:
                        - Mode bits used to set permissions on created files by default.
                        - Must be an octal value between 0000 and 0777 or a decimal value between 0 and 511.
                        - Directories within the path are not affected by this setting.
                        - This might be in conflict with other options that affect the file mode, like fsGroup, and
                          the result can be other mode bits set.
                        type: str
                        default: '0644'
                    items:
                        description:
                        - If unspecified, each key-value pair in the Data field of the referenced ConfigMap will be
                          projected into the volume as a file whose name is the key and content is the value.
                        - If specified, the listed keys will be projected into the specified paths, and unlisted keys
                          will not be present.
                        - If a key is specified which is not present in the ConfigMap, the volume setup will error
                          unless it is marked optional.
                        - Paths must be relative and may not contain the '..' path or start with '..'.
                        type: list
                        elements: dict
                        suboptions:
                            key:
                                description:
                                - The key to project.
                                type: str
                                required: true
                            path:
                                description:
                                - The relative path of the file to map the key to.
                                - May not be an absolute path.
                                - May not contain the path element '..'.
                                - May not start with the string '..'.
                                type: str
                                required: true
                            mode:
                                description:
                                - Mode bits used to set permissions on this file.
                                - Must be an octal value between 0000 and 0777 or a decimal value between 0 and 511.
                                - If not specified, the volume I(default_mode) will be used.
                                - This might be in conflict with other options that affect the file mode, like fsGroup,
                                  and the result can be other mode bits set.
                                type: str
            secret:
                description:
                - Adapts a Secret into a volume.
                - The contents of the target Secret's Data field will be presented in a volume as files using the
                  keys in the C(Data) field as the file names, unless the items element is populated with specific
                  mappings of keys to paths.
                - Secret volumes support ownership management and SELinux relabeling.
                type: dict
                suboptions:
                    name:
                        description:
                        - Name of the secret in the pod's namespace to use.
                        - More info U(https://kubernetes.io/docs/concepts/storage/volumes#secret)
                        type: str
                    optional:
                        description:
                        - Specify whether the Secret or its keys must be defined.
                        type: bool
                    default_mode:
                        description:
                        - Mode bits used to set permissions on created files by default.
                        - Must be an octal value between 0000 and 0777 or a decimal value between 0 and 511.
                        - Directories within the path are not affected by this setting.
                        - This might be in conflict with other options that affect the file mode, like fsGroup, and
                          the result can be other mode bits set.
                        type: str
                        default: '0644'
                    items:
                        description:
                        - If unspecified, each key-value pair in the Data field of the referenced Secret will be
                          projected into the volume as a file whose name is the key and content is the value.
                        - If specified, the listed keys will be projected into the specified paths, and unlisted keys
                          will not be present.
                        - If a key is specified which is not present in the Secret, the volume setup will error
                          unless it is marked optional.
                        - Paths must be relative and may not contain the '..' path or start with '..'.
                        type: list
                        elements: dict
                        suboptions:
                            key:
                                description:
                                - The key to project.
                                type: str
                                required: true
                            path:
                                description:
                                - The relative path of the file to map the key to.
                                - May not be an absolute path.
                                - May not contain the path element '..'.
                                - May not start with the string '..'.
                                type: str
                                required: true
                            mode:
                                description:
                                - Mode bits used to set permissions on this file.
                                - Must be an octal value between 0000 and 0777 or a decimal value between 0 and 511.
                                - If not specified, the volume I(default_mode) will be used.
                                - This might be in conflict with other options that affect the file mode, like fsGroup,
                                  and the result can be other mode bits set.
                                type: str
    replicas:
        description:
        - Number of desired pods.
        - This is a pointer to distinguish between explicit zero and not specified.
        type: int
        default: 1
    min_ready_seconds:
        description:
        - Minimum number of seconds for which a newly created pod should be ready without any of its container crashing,
          for it to be considered available.
        - I(min_ready_seconds=0) means pod will be considered available as soon as it is ready.
        type: int
        default: 0
    strategy:
        description:
        - The deployment strategy to use to replace existing pods with new ones.
        type: dict
        suboptions:
            type:
                description:
                - Type of deployment strategy.
                type: str
                default: RollingUpdate
                choices: [ Recreate, RollingUpdate]
            max_surge:
                description:
                - Rolling update config param.
                - The maximum number of pods that can be scheduled above the desired number of pods.
                - Value can be an absolute number (ex. C(5)) or a percentage of desired pods (ex. C(10%)).
                - This can not be 0 if I(max_unavailable=0).
                - Absolute number is calculated from percentage by rounding up.
                type: str
                default: 25%
            max_unavailable:
                description:
                - Rolling update config param.
                - The maximum number of pods that can be unavailable during the update.
                - Value can be an absolute number (ex. C(5)) or a percentage of desired pods (ex. C(10%)).
                - Absolute number is calculated from percentage by rounding down.
                - This can not be 0 if C(max_surge=0).
                type: str
                default: 25%
    revision_history_limit:
        description:
        - The number of old ReplicaSets to retain to allow rollback.
        - This is a pointer to distinguish between explicit zero and not specified.
        type: int
        default: 10
    progress_deadline_seconds:
        description:
        - The maximum time in seconds for a deployment to make progress before it is considered to be failed.
        - The deployment controller will continue to process failed deployments and a condition with a
          ProgressDeadlineExceeded reason will be surfaced in the deployment status.
        - Note that progress will not be estimated during the time a deployment is paused.
        type: int
        default: 600
    paused:
        description:
        - Indicates that the deployment is paused.
        type: bool
        default: false
author:
    - Mihael Trajbarič (@mihaTrajbaric)
'''
# TODO examples
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
from ansible_collections.sodalite.k8s.plugins.module_utils.args_common import update_arg_spec
from ansible_collections.sodalite.k8s.plugins.module_utils.common import Validators, CommonValidation
from ansible_collections.sodalite.k8s.plugins.module_utils.helper import clean_dict
from copy import deepcopy


def definition(params):

    body = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": params.get('name'),
            "labels": params.get('labels'),
            "annotations": params.get('annotations')
        },
        "spec": {
            'selector': {
                'matchExpressions': (params.get('selector') or {}).get('match_expressions'),
                'matchLabels': (params.get('selector') or {}).get('match_labels')
            },
            "template": {
                "metadata": {
                    "name": params.get('name'),
                    "labels": params.get('labels'),
                    "annotations": params.get('annotations')
                },
                'spec': {
                    'containers': [
                        {
                            'name': container.get('name'),
                            'image': container.get('image'),
                            'imagePullPolicy': container.get('image_pull_policy'),
                            'command': container.get('command'),
                            'args': container.get('args'),
                            'workingDir': container.get('working_dir'),
                            'ports': [
                                {
                                    'containerPort': port.get('container_port'),
                                    'hostIP': port.get('host_ip'),
                                    'hostPort': port.get('host_port'),
                                    'name': port.get('name'),
                                    'protocol': port.get('protocol'),
                                }
                                for port in container.get('ports')
                            ],
                            'env': [
                                {
                                    'name': env_var.get('name'),
                                    'valueFrom': {
                                        'configMapKeyRef': env_var.get('config_map'),
                                        'secretKeyRef': env_var.get('secret'),
                                    },
                                    'value': env_var.get('value')
                                }
                                for env_var in container.get('env')
                            ],
                            'envFrom': [
                                {
                                    'configMapRef': env_from_item.get('config_map'),
                                    'prefix': env_from_item.get('prefix'),
                                    'secretRef': env_from_item.get('secret'),
                                }
                                for env_from_item in container.get('env_from')
                            ],
                            'volumeMounts': [
                                {
                                    'mountPath': volume_mount.get('path'),
                                    'name': volume_mount.get('name'),
                                    'mountPropagation': volume_mount.get('propagation'),
                                    'readOnly': volume_mount.get('read_only'),
                                    'subPath': volume_mount.get('sub_path'),
                                    'subPathExpr': volume_mount.get('sub_path_expr'),
                                }
                                for volume_mount in container.get('volume_mounts')
                            ],
                            'volumeDevices': [
                                {
                                    'devicePath': volume_device.get('path'),
                                    'name': volume_device.get('name')
                                }
                                for volume_device in container.get('volume_devices')
                            ],
                            'resources': {
                                'limits': container.get('resource_limits'),
                                'requests': container.get('resource_requests')
                            }
                        }
                        for container in params.get('containers')
                    ],
                    'imagePullSecrets': [{'name': secret} for secret in params.get('image_pull_secrets')],
                    'enableServiceLinks': params.get('enable_service_links'),
                    'volumes': [
                        {
                            'name': volume.get('name'),
                            'persistentVolumeClaim': {
                                'claimName': (volume.get('pvc') or {}).get('claim_name'),
                                'readOnly': (volume.get('pvc') or {}).get('read_only')
                            },
                            'configMap': {
                                'name': (volume.get('config_map') or {}).get('name'),
                                'optional': (volume.get('config_map') or {}).get('optional'),
                                'defaultMode': (volume.get('config_map') or {}).get('default_mode'),
                                'items': (volume.get('config_map') or {}).get('items'),
                            },
                            'secret': {
                                'secretName': (volume.get('secret') or {}).get('name'),
                                'optional': (volume.get('secret') or {}).get('optional'),
                                'defaultMode': (volume.get('secret') or {}).get('default_mode'),
                                'items': (volume.get('secret') or {}).get('items'),
                            }
                        }
                        for volume in params.get('volumes')
                    ]
                }
            },
            'replicas': params.get('replicas'),
            'minReadySeconds': params.get('min_ready_seconds'),
            'strategy': {
                "type": (params.get('strategy') or {}).get('type'),
                "rollingUpdate": {
                    "maxSurge": (params.get('strategy') or {}).get('max_surge'),
                    "maxUnavailable": (params.get('strategy') or {}).get('max_unavailable'),
                }
            },
            'revisionHistoryLimit': params.get('revision_history_limit'),
            'progressDeadlineSeconds': params.get('progress_deadline_seconds'),
            'paused': params.get('paused')
        }

    }
    return clean_dict(body)


def validate(module, k8s_definition):
    # TODO implement

    CommonValidation.metadata(module, k8s_definition)
    #
    # spec_keys = list(k8s_definition['spec'].keys())
    #
    # access_modes = k8s_definition['spec'].get('accessModes', list())
    # if not access_modes:
    #     module.fail_json(msg="Access_modes should have at least 1 element")
    #
    # access_modes_valid = all([item in ('ReadWriteOnce', 'ReadOnlyMany', 'ReadWriteMany') for item in access_modes])
    # if not access_modes_valid:
    #     module.fail_json(msg="Elements of access_modes should be chosen from "
    #                          "('ReadWriteOnce', 'ReadOnlyMany', 'ReadWriteMany')")
    #
    # if 'selector' in spec_keys:
    #     match_expressions = k8s_definition['spec']['selector'].get('matchExpressions', list())
    #     for expression in match_expressions:
    #         valid_keys = ('In', 'NotIn', 'Exists', 'DoesNotExist')
    #         operator = expression.get('operator')
    #         if operator not in valid_keys:
    #             module.fail_json(msg="Every selector.match_expressions.key should be chosen "
    #                                  "from {0}".format({', '.join(valid_keys)}))
    #         values_condition = (operator in ('In', 'NotIn')) == bool(expression.get('values'))
    #         if not values_condition:
    #             module.fail_json(msg="If in any selector.match_expressions operator is 'In' or 'NotIn', the values "
    #                                  "array must be non-empty. If operator is 'Exists' or 'DoesNotExist', the values "
    #                                  "array must be empty.")
    #     match_labels = k8s_definition['spec']['selector'].get('matchLabels', dict())
    #     if not Validators.string_string_dict(match_labels):
    #         module.fail_json(msg="Selector.match_labels should be map[string]string")
    #
    # if 'resources' in spec_keys:
    #     limits = k8s_definition['spec']['resources'].get('limits', dict())
    #     if not Validators.string_quantity_dict(limits):
    #         module.fail_json(msg="Storage_limit should be map[string]Quantity")
    #
    #     requests = k8s_definition['spec']['resources'].get('requests', dict())
    #     if not Validators.string_quantity_dict(requests):
    #         module.fail_json(msg="Storage_request should be map[string]Quantity")


def main():
    argspec = update_arg_spec()
    argspec.update(dict(
        selector=dict(type='dict', options=dict(
            match_labels=dict(type='dict'),
            match_expressions=dict(type='list', elements='dict', options=dict(
                key=dict(type='str', required=True, no_log=False),
                operator=dict(type='str', required=True, choices=['In', 'NotIn', 'Exists', 'DoesNotExist']),
                values=dict(type='list', elements='str')
            ))
        )),
        # TODO container, init_container spec
        containers=dict(type='list', elements='dict', options=dict(
            # TODO validate DNS for name
            name=dict(type='str', required=True),
            image=dict(type='str'),
            # TODO Defaults to Always if :latest tag is specified, or IfNotPresent otherwise
            image_pull_policy=dict(type='str', choices=['Always', 'Never', 'IfNotPresent']),
            command=dict(type='list', elements='str'),
            args=dict(type='list', elements='str'),
            working_dir=dict(type='str', aliases=['workdir']),
            ports=dict(type='list', elements='dict', options=dict(
                # TODO validate all ports (0 < x < 65536)
                container_port=dict(type='int', required=True),
                host_ip=dict(type='str'),
                host_port=dict(type='int'),
                # TODO IANA_SVC_NAME, unique inside pod
                name=dict(type='str'),
                protocol=dict(type='str', choices=['UDP', 'TCP', 'SCTP'], default='TCP')
            )),
            env=dict(type='list', elements='dict', options=dict(
                # TODO validate C_IDENTIFIER

                name=dict(type='str', required=True),
                value=dict(type='str'),
                config_map=dict(type='dict', options=dict(
                    key=dict(type='str', required=True, no_log=False),
                    # TODO validate lowercase subdomain (name)
                    name=dict(type='str'),
                    optional=dict(type='bool')
                )),
                # TODO resources_field_ref, field_ref
                # TODO this must be validated.
                #  value, valueFrom.configMapKeyRef and  valueFrom.secretKeyRef are exclusive
                secret=dict(type='dict', no_log=False, options=dict(
                    key=dict(type='str', required=True, no_log=False),
                    # TODO validate lowercase subdomain (name)
                    name=dict(type='str'),
                    optional=dict(type='bool')
                ))
            )),
            env_from=dict(type='list', elements='dict', options=dict(
                # TODO this must be validate.
                #  configMapKeyRef and secretKeyRef are mutually exclusive
                config_map=dict(type='dict', options=dict(
                    # TODO required?
                    # TODO validate lowercase subdomain (name)
                    name=dict(type='str'),
                    optional=dict(type='bool')
                )),
                # TODO validate C_IDENTIFIER
                prefix=dict(type='str'),
                secret=dict(type='dict', no_log=False, options=dict(
                    # TODO required?
                    # TODO validate lowercase subdomain (name)
                    name=dict(type='str'),
                    optional=dict(type='bool')
                ))
            )),
            volume_mounts=dict(type='list', elements='dict', options=dict(
                # TODO validate must not contain ':'
                path=dict(type='str', required=True),
                name=dict(type='str', required=True),
                propagation=dict(type='str', choices=['None', 'HostToContainer', 'Bidirectional'], default='None'),
                read_only=dict(type='bool', default=False),
                # TODO validate mutually exclusive (sub_path, sub_path_expr)
                sub_path=dict(type='str'),
                sub_path_expr=dict(type='str')
            )),
            # TODO validate name matches name in volumes
            # TODO validate only pvc, not other modes
            volume_devices=dict(type='list', elements='dict', options=dict(
                # TODO validate must not contain ':'?
                path=dict(type='str', required=True),
                name=dict(type='str', required=True)
            )),
            resource_limits=dict(type='dict', options=dict(
                # TODO validate quantity
                cpu=dict(type='str'),
                memory=dict(type='str')
                # TODO could also add hugepages
            )),
            resource_requests=dict(type='dict', options=dict(
                # TODO validate quantity
                cpu=dict(type='str'),
                memory=dict(type='str')
                # TODO could also add hugepages
            ))
            # TODO add lifecycle, livenessProbe, readinessProbe, startupProbe, securityContext, stdin, stdinOnce,
            #      terminationMessagePath, terminationMessagePolicy, tty
        )),
        # init_containers=dict(type='list', elements='dict', options=deepcopy({})),
        # TODO wtf is this?
        image_pull_secrets=dict(type='list', elements='str', no_log=False),
        enable_service_links=dict(type='bool', default=True),
        volumes=dict(type='list', elements='dict', options=dict(
            # TODO validate DNS_LABEL
            # TODO validate only one type (pvc, config_map, secret)
            name=dict(type='str', required=True),
            pvc=dict(type='dict', options=dict(
                claim_name=dict(type='str', required=True),
                read_only=dict(type='bool', default=False)
            )),
            config_map=dict(type='dict', options=dict(
                name=dict(type='str'),
                optional=dict(type='bool'),
                default_mode=dict(type='int', default=0o644),
                items=dict(type='list', elements='dict', options=dict(
                    key=dict(type='str', required=True, no_log=False),
                    path=dict(type='str', required=True),
                    mode=dict(type='int')
                ))
            )),
            secret=dict(type='dict', no_log=False, options=dict(
                name=dict(type='str'),
                optional=dict(type='bool'),
                default_mode=dict(type='int', default=0o644),
                items=dict(type='list', elements='dict', options=dict(
                    key=dict(type='str', required=True, no_log=False),
                    path=dict(type='str', required=True),
                    mode=dict(type='int')
                ))
            ))
        )),
        # TODO anything else
        # TODO lifecycle params
        # TODO maybe scheduling
        replicas=dict(type='int', default=1),
        min_ready_seconds=dict(type='int', default=0),
        strategy=dict(type='dict', options=dict(
            type=dict(type='str', choices=['Recreate', 'RollingUpdate'], default='RollingUpdate'),
            # TODO params required if RollingUpdate
            max_surge=dict(type='str', default='25%'),
            max_unavailable=dict(type='str', default='25%')
        )),
        revision_history_limit=dict(type='int', default=10),
        progress_deadline_seconds=dict(type='int', default=600),
        paused=dict(type='bool', default=False),
    ))
    # required_if = [
    #     ('state', 'present', ('access_modes', 'storage_request'))
    # ]

    module = AnsibleModule(argument_spec=argspec,
                           # required_if=required_if,
                           supports_check_mode=True)
    from ansible_collections.sodalite.k8s.plugins.module_utils.k8s_connector import execute_module

    volume_claim_def = definition(module.params)
    # if module.params.get('state') != 'absent':
    #     validate(module, volume_claim_def)

    # import json
    # module.exit_json(msg=json.dumps(volume_claim_def, indent=2))

    execute_module(module, volume_claim_def)


if __name__ == '__main__':
    main()
