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
    - sodalite.k8s.metadata_options
    - kubernetes.core.k8s_auth_options
    - kubernetes.core.k8s_wait_options
    - kubernetes.core.k8s_delete_options

options:
    selector:
        description:
        - A label query over a set of resources.
        - The result of C(match_labels) and C(match_expressions) are ANDed.
        - An empty label selector matches all objects.
        - A null label selector matches no objects.
        type: dict
        required: true
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
    containers:
        description:
        - List of containers belonging to the pod.
        - There must be at least one container in a Pod.
        type: list
        elements: dict
        required: true
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
                                required: true
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
                                required: true
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
                    sub_path_expr:
                        description:
                        - Expanded path within the volume from which the container's volume should be mounted.
                        - Behaves similarly to I(sub_path) but environment variable references $(VAR_NAME) are expanded
                          using the container's environment.
                        - "\"\" means volume's root."
                        - I(sub_path_expr) and I(sub_path) are mutually exclusive.
                        type: str
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
                        type: int
                        default: 0644
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
                                type: int
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
                        type: int
                        default: 0644
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
                                type: int
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
                - Present only if I(type = RollingUpdate)
                - The maximum number of pods that can be scheduled above the desired number of pods.
                - Value can be an absolute number (ex. C(5)) or a percentage of desired pods (ex. C(10%)).
                - This can not be 0 if I(max_unavailable=0).
                - Absolute number is calculated from percentage by rounding up.
                type: str
            max_unavailable:
                description:
                - Rolling update config param.
                - Present only if I(type = RollingUpdate)
                - The maximum number of pods that can be unavailable during the update.
                - Value can be an absolute number (ex. C(5)) or a percentage of desired pods (ex. C(10%)).
                - Absolute number is calculated from percentage by rounding down.
                - This can not be 0 if C(max_surge=0).
                type: str
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

seealso:
- name: K8s Deployment documentation
  description: Documentation about Deployment concept on kubernetes website
  link: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
- name: K8s Deployment API reference
  description: API reference for K8s Deployment resource on kubernetes website
  link: https://kubernetes.io/docs/reference/kubernetes-api/workload-resources/deployment-v1/


author:
    - Mihael Trajbarič (@mihaTrajbaric)
'''

EXAMPLES = r'''
# Create getting-started deployment
- name: Minimal example
  sodalite.k8s.deployment:
    name: getting-started
    state: present
    labels:
      app: getting-started
    selector:
      match_labels:
        app: getting-started
    replicas: 1
    containers:
      - name: getting-started-container
        image: docker/getting-started

# Customize command, args, workdir
- name: Minimal example
  sodalite.k8s.deployment:
    name: getting-started
    state: present
    labels:
      app: getting-started
    selector:
      match_labels:
        app: getting-started
    containers:
      - name: getting-started-container
        image: docker/getting-started
        image_pull_policy: Always
        workdir: /app
        command: ["node"]
        args: ["src/index.js"]

# Open ports
- name: Minimal example with ports
  sodalite.k8s.deployment:
    name: getting-started
    state: present
    labels:
      app: getting-started
    selector:
      match_labels:
        app: getting-started
    containers:
      - name: getting-started-container
        image: docker/getting-started
        ports:
          - name: http-port
            host_port: 80
            container_port: 80
            protocol: TCP
          - name: another-port
            host_port: 5432
            container_port: 5432
            protocol: UDP

# Add environment #1
- name: Minimal example with environment
  sodalite.k8s.deployment:
    name: getting-started
    state: present
    labels:
      app: getting-started
    selector:
      match_labels:
        app: getting-started
    containers:
      - name: getting-started-container
        image: docker/getting-started
        env:
          - name: DB_PORT
            value: 5432
          - name: DB_PORT_2
            config_map:
              name: postgres-db-config
              key: PORT
          - name: DB_PASSWORD
            secret:
              name: postgres-db-secret
              key: PASSWORD

# Add environment #2
- name: Minimal example with env_from
  sodalite.k8s.deployment:
    name: getting-started
    state: present
    labels:
      app: getting-started
    selector:
      match_labels:
        app: getting-started
    containers:
      - name: getting-started-container
        image: docker/getting-started
        env_from:
          - config_map:
              name: postgres-db-config
            prefix: DB_1_
          - secret:
              name: db_2_secret
            prefix: DB_2_

# Volumes
- name: Minimal example
  sodalite.k8s.deployment:
    name: getting-started
    state: present
    labels:
      app: getting-started
    selector:
      match_labels:
        app: getting-started
    containers:
      - name: getting-started-container
        image: docker/getting-started
        volume_mounts:
          - name: my-volume
            path: /home/test_volume
            propagation: HostToContainer
            read_only: no
            sub_path: foo/bar/
          - name: my-volume-2
            path: /home/test_volume_2
            propagation: HostToContainer
            read_only: no
            sub_path_expr: foo/bar/$(VAR_NAME)
        volume_devices:
          - name: my-volume-device
            path: /home/volume_device
    volumes:
      - name: my-volume-device
        pvc:
          claim_name: my_persistent_volume_claim
          read_only: yes
      - name: my-volume
        config_map:
          name: config_map_for_volume
          optional: true
          default_mode: 0644
          items:
            - key: DB_info
              path: volume/db_info.json
              mode: 0644
      - name: my-volume-2
        secret:
          name: secret_for_volume
          optional: true
          default_mode: 0644
          items:
            - key: DB_info
              path: volume/db_info_2.json
              mode: 0644

# Resource limits and requests
- name: Minimal example with limits and requests
  sodalite.k8s.deployment:
    name: getting-started
    state: present
    labels:
      app: getting-started
    selector:
      match_labels:
        app: getting-started
    containers:
      - name: getting-started-container
        image: docker/getting-started
        resource_limits:
          cpu: 1
          memory: 4Gi
        resource_requests:
          cpu: 0.1
          memory: 2Gi

# k8s options
- name: Minimal example with k8s options
  sodalite.k8s.deployment:
    name: getting-started
    state: present
    labels:
      app: getting-started
    selector:
      match_labels:
        app: getting-started
    containers:
      - name: getting-started-container
        image: docker/getting-started
    # only DockerConfig type secrets are honored
    image_pull_secrets:
        - myregistrykey
    # enabled by default
    enable_service_links: no
    replicas: 3
    min_ready_seconds: 30
    strategy:
        type: RollingUpdate
        max_surge: 30%
        max_unavailable: 30%
    revision_history_limit: 7
    progress_deadline_seconds: 800
    paused: false

# Remove Deployment
- name: Remove deployment
  sodalite.k8s.deployment:
    name: getting-started
    state: absent
    selector:
      match_labels:
        app: getting-started
    containers:
      - name: getting-started-container
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
                                for port in container.get('ports') or list()
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
                                for env_var in container.get('env') or list()
                            ],
                            'envFrom': [
                                {
                                    'configMapRef': env_from_item.get('config_map'),
                                    'prefix': env_from_item.get('prefix'),
                                    'secretRef': env_from_item.get('secret'),
                                }
                                for env_from_item in container.get('env_from') or list()
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
                                for volume_mount in container.get('volume_mounts') or list()
                            ],
                            'volumeDevices': [
                                {
                                    'devicePath': volume_device.get('path'),
                                    'name': volume_device.get('name')
                                }
                                for volume_device in container.get('volume_devices') or list()
                            ],
                            'resources': {
                                'limits': container.get('resource_limits'),
                                'requests': container.get('resource_requests')
                            }
                        }
                        for container in params.get('containers') or list()
                    ],
                    'imagePullSecrets': [{'name': secret} for secret in params.get('image_pull_secrets') or list()],
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
                        for volume in params.get('volumes') or list()
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

    CommonValidation.metadata(module, k8s_definition)
    CommonValidation.selector(module, k8s_definition)

    if not Validators.dns_subdomain(k8s_definition['metadata']['name']):
        module.fail_json(msg=f"'name' {Validators.dns_subdomain_msg}")

    strategy = k8s_definition.get('spec').get('strategy')
    if strategy and strategy['type'] == 'Recreate' and 'rollingUpdate' in strategy.keys():
        module.fail_json(msg="strategy.max_surge and strategy.max_unavailable can only be present "
                             "if strategy.type==RollingUpdate")

    pod_definition = k8s_definition['spec']['template']
    CommonValidation.metadata(module, pod_definition)

    # to verify unique port names
    port_names = list()
    containers = pod_definition['spec'].get('containers') or list()

    if len(containers) < 1:
        module.fail_json(msg="There must be at least one container in a Pod.")

    for i, container in enumerate(containers):
        if not Validators.dns_label(container['name']):
            module.fail_json(msg=f"containers[{i}].name {Validators.dns_label_msg}")

        if 'image' not in container.keys():
            module.fail_json(msg=f"containers[{i}].image is missing")

        for j, port in enumerate(container.get('ports', list())):
            if not Validators.port(port.get('containerPort')):
                module.fail_json(msg=f"containers[{i}].ports[{j}].container_port {Validators.port_msg}")
            if not Validators.port(port.get('hostPort')):
                module.fail_json(msg=f"containers[{i}].ports[{j}].host_port {Validators.port_msg}")
            name = port.get('name')
            if not Validators.iana_svc_name(name):
                module.fail_json(msg=f"containers[{i}].ports[{j}].name {Validators.iana_svc_name_msg}")
            if name in port_names:
                module.fail_json(msg=f"Duplicate port name found (containers[{i}].ports[{j}].name)."
                                     f" Each named port in a pod must have a unique name")
            if name:
                port_names.append(name)

        for j, env_var in enumerate(container.get('env', list())):
            if not Validators.c_identifier(env_var.get('name')):
                module.fail_json(msg=f"containers[{i}].env[{j}].name {Validators.c_identifier_msg}")
            modes = [
                'value' in env_var,
                'configMapKeyRef' in env_var.get('valueFrom', {}),
                'secretKeyRef' in env_var.get('valueFrom', {})
            ]
            if sum(modes) != 1:
                module.fail_json(msg=f"More then one value source in containers[{i}].env[{j}]. "
                                     f"Only one of (value, config_map, secret) can be present.")

            if not Validators.dns_subdomain(env_var.get('valueFrom', {}).get('configMapKeyRef', {}).get('name')):
                module.fail_json(msg=f"containers[{i}].env[{j}].config_map.name {Validators.dns_subdomain_msg}")

            if not Validators.dns_subdomain(env_var.get('valueFrom', {}).get('secretKeyRef', {}).get('name')):
                module.fail_json(msg=f"containers[{i}].env[{j}].secret.name {Validators.dns_subdomain_msg}")

        for j, env_from_item in enumerate(container.get('envFrom', list())):
            modes = [
                'configMapRef' in env_from_item,
                'secretRef' in env_from_item
            ]
            if sum(modes) != 1:
                module.fail_json(msg=f"More then one value source in containers[{i}].env_from[{j}]. "
                                     f"Only one of (config_map, secret) can be present.")

            if not Validators.dns_subdomain(env_from_item.get('configMapRef', {}).get('name')):
                module.fail_json(msg=f"containers[{i}].env_from[{j}].config_map.name {Validators.dns_subdomain_msg}")

            if not Validators.dns_subdomain(env_from_item.get('secretRef', {}).get('name')):
                module.fail_json(msg=f"containers[{i}].env_from[{j}].secret.name {Validators.dns_subdomain_msg}")

            if not Validators.c_identifier(env_from_item.get('prefix')):
                module.fail_json(msg=f"containers[{i}].env_from[{j}].prefix {Validators.c_identifier_msg}")

        # dict of <volume_name>: <volume_type>
        volumes = pod_definition['spec'].get('volumes') or list()
        volume_dict = {volume['name']: next(iter((volume.keys() - {'name'})))
                       for volume in volumes}
        for j, volume_mount in enumerate(container.get('volumeMounts', list())):
            if volume_mount.get('name') not in volume_dict.keys():
                module.fail_json(msg=f"containers[{i}].volume_mounts[{j}].name not found. Every name should match the "
                                     f"Name of a Volume.")
            if ':' in volume_mount.get('mountPath'):
                module.fail_json(msg=f"containers[{i}].volume_mounts[{j}].path should not contain ':'")

            sub_path_mutually_exclusive_violation = sum(['subPath' in volume_mount, 'subPathExpr' in volume_mount]) > 1
            if sub_path_mutually_exclusive_violation:
                module.fail_json(msg=f"sub_path and sub_path_expr in containers[{i}].volume_mounts[{j}] are mutually"
                                     f" exclusive")

        for j, volume_device in enumerate(container.get('volumeDevices', list())):
            name = volume_device.get('name')
            if name not in volume_dict.keys():
                module.fail_json(msg=f"containers[{i}].volume_devices[{j}].name not found. Every name should match the "
                                     f"Name of a Volume.")
            elif volume_dict.get(name) != 'persistentVolumeClaim':
                module.fail_json(msg=f"containers[{i}].volume_devices[{j}].name should match the name of a "
                                     f"persistentVolumeClaim (pvc) in the pod")

            if ':' in volume_device.get('devicePath'):
                module.fail_json(msg=f"containers[{i}].volume_devices[{j}].path should not contain ':'")

        if not Validators.string_quantity_dict((container.get('resources') or {}).get('limits')):
            module.fail_json(msg="resource_limits.cpu and resource_limits.memory should be Quantities")

        if not Validators.string_quantity_dict((container.get('resources') or {}).get('requests')):
            module.fail_json(msg="resource_requests.cpu and resource_requests.memory should be Quantities")

    for i, volume in enumerate(pod_definition['spec'].get('volumes') or list()):
        if not Validators.dns_label(volume['name']):
            module.fail_json(msg=f"volumes[{i}].name {Validators.dns_label_msg}")

        modes = [
            'persistentVolumeClaim' in volume,
            'configMap' in volume,
            'secret' in volume
        ]
        if sum(modes) != 1:
            module.fail_json(msg=f"More then one volume source in volumes[{i}]. "
                                 f"Only one of (pvc, config_map, secret) can be present.")


def main():
    argspec = update_arg_spec()
    argspec.update(dict(
        selector=dict(type='dict', required=True, options=dict(
            match_labels=dict(type='dict'),
            match_expressions=dict(type='list', elements='dict', options=dict(
                key=dict(type='str', required=True, no_log=False),
                operator=dict(type='str', required=True, choices=['In', 'NotIn', 'Exists', 'DoesNotExist']),
                values=dict(type='list', elements='str')
            ))
        )),
        # TODO init_container spec
        containers=dict(type='list', required=True, elements='dict', options=dict(
            name=dict(type='str', required=True),
            image=dict(type='str'),
            image_pull_policy=dict(type='str', choices=['Always', 'Never', 'IfNotPresent']),
            command=dict(type='list', elements='str'),
            args=dict(type='list', elements='str'),
            working_dir=dict(type='str', aliases=['workdir']),
            ports=dict(type='list', elements='dict', options=dict(
                container_port=dict(type='int', required=True),
                host_ip=dict(type='str'),
                host_port=dict(type='int'),
                name=dict(type='str'),
                protocol=dict(type='str', choices=['UDP', 'TCP', 'SCTP'], default='TCP')
            )),
            env=dict(type='list', elements='dict', options=dict(
                name=dict(type='str', required=True),
                value=dict(type='str'),
                config_map=dict(type='dict', options=dict(
                    key=dict(type='str', required=True, no_log=False),
                    name=dict(type='str'),
                    optional=dict(type='bool')
                )),
                # TODO resources_field_ref, field_ref
                secret=dict(type='dict', no_log=False, options=dict(
                    key=dict(type='str', required=True, no_log=False),
                    name=dict(type='str'),
                    optional=dict(type='bool')
                ))
            )),
            env_from=dict(type='list', elements='dict', options=dict(
                config_map=dict(type='dict', options=dict(
                    name=dict(type='str', required=True),
                    optional=dict(type='bool')
                )),
                prefix=dict(type='str'),
                secret=dict(type='dict', no_log=False, options=dict(
                    name=dict(type='str', required=True),
                    optional=dict(type='bool')
                ))
            )),
            volume_mounts=dict(type='list', elements='dict', options=dict(
                path=dict(type='str', required=True),
                name=dict(type='str', required=True),
                propagation=dict(type='str', choices=['None', 'HostToContainer', 'Bidirectional'], default='None'),
                read_only=dict(type='bool', default=False),
                sub_path=dict(type='str'),
                sub_path_expr=dict(type='str')
            )),
            volume_devices=dict(type='list', elements='dict', options=dict(
                path=dict(type='str', required=True),
                name=dict(type='str', required=True)
            )),
            resource_limits=dict(type='dict', options=dict(
                cpu=dict(type='str'),
                memory=dict(type='str')
                # TODO could also add hugepages
            )),
            resource_requests=dict(type='dict', options=dict(
                cpu=dict(type='str'),
                memory=dict(type='str')
                # TODO could also add hugepages
            ))
            # TODO add lifecycle, livenessProbe, readinessProbe, startupProbe, securityContext, stdin, stdinOnce,
            #      terminationMessagePath, terminationMessagePolicy, tty
        )),
        image_pull_secrets=dict(type='list', elements='str', no_log=False),
        enable_service_links=dict(type='bool', default=True),
        volumes=dict(type='list', elements='dict', options=dict(
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
        # TODO lifecycle, scheduling
        replicas=dict(type='int', default=1),
        min_ready_seconds=dict(type='int', default=0),
        strategy=dict(type='dict', options=dict(
            type=dict(type='str', choices=['Recreate', 'RollingUpdate'], default='RollingUpdate'),
            max_surge=dict(type='str'),
            max_unavailable=dict(type='str')
        )),
        revision_history_limit=dict(type='int', default=10),
        progress_deadline_seconds=dict(type='int', default=600),
        paused=dict(type='bool', default=False),
    ))
    required_if = [
        ('state', 'present', ('labels',))
    ]

    module = AnsibleModule(argument_spec=argspec,
                           required_if=required_if,
                           mutually_exclusive=UPDATE_MUTUALLY_EXCLUSIVE,
                           supports_check_mode=True)
    from ansible_collections.sodalite.k8s.plugins.module_utils.k8s_connector import execute_module

    k8s_def = definition(module.params)
    if module.params.get('state') != 'absent':
        validate(module, k8s_def)

    execute_module(module, k8s_def)


if __name__ == '__main__':
    main()
