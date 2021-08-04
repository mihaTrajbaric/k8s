# SODALITE k8s collection
<!-- Add CI and code coverage badges here. Samples included below. -->
[![CI](https://github.com/mihaTrajbaric/k8s/actions/workflows/ansible-test.yml/badge.svg?event=push)](https://github.com/mihaTrajbaric/k8s/actions/workflows/ansible-test.yml) [![codecov](https://codecov.io/gh/mihaTrajbaric/k8s/branch/main/graph/badge.svg?token=MHBEH17281)](https://codecov.io/gh/mihaTrajbaric/k8s)

<!-- Describe the collection and why a user would want to use it. What does the collection do? -->

This repository hosts the `sodalite.k8s` Ansible Collection.

The collection includes quality Ansible content to help automate the management of applications in Kubernetes

<!--start requires_ansible-->
## Ansible version compatibility

This collection has been tested against following Ansible versions: **>=2.9.17**.

Plugins and modules within a collection may be tested with only specific Ansible versions.
A collection may contain metadata that identifies these versions.
PEP440 is the schema used to describe the versions of Ansible.
<!--end requires_ansible-->

## Python Support

* Collection supports 3.6+

Note: Python2 is deprecated from [1st January 2020](https://www.python.org/doc/sunset-python-2/). Please switch to Python3.

## External requirements

Collection requires python package [kubernetes>=12.0.0](https://pypi.org/project/kubernetes/).

## Included content

<!--start collection content-->
### Modules
Name | Description
--- | ---
[sodalite.k8s.config_map](https://github.com/mihaTrajbaric/k8s/blob/main/docs/sodalite.k8s.config_map_module.rst)|Creates k8s ConfigMap
[sodalite.k8s.deployment](https://github.com/mihaTrajbaric/k8s/blob/main/docs/sodalite.k8s.deployment_module.rst)|Creates k8s Deployment
[sodalite.k8s.ingress](https://github.com/mihaTrajbaric/k8s/blob/main/docs/sodalite.k8s.ingress_module.rst)|Creates k8s Ingress
[sodalite.k8s.namespace](https://github.com/mihaTrajbaric/k8s/blob/main/docs/sodalite.k8s.namespace_module.rst)|Creates k8s Namespace
[sodalite.k8s.pvc](https://github.com/mihaTrajbaric/k8s/blob/main/docs/sodalite.k8s.pvc_module.rst)|Creates k8s PersistentVolumeClaim
[sodalite.k8s.secret](https://github.com/mihaTrajbaric/k8s/blob/main/docs/sodalite.k8s.secret_module.rst)|Creates k8s Secret
[sodalite.k8s.service](https://github.com/mihaTrajbaric/k8s/blob/main/docs/sodalite.k8s.service_module.rst)|Creates k8s Service
[sodalite.k8s.storage_class](https://github.com/mihaTrajbaric/k8s/blob/main/docs/sodalite.k8s.storage_class_module.rst)|Creates k8s StorageClass

<!--end collection content-->

## Installation and Usage

### Installing the Collection from GIT repository

Before using the Sodalite.8s collection, you need to install it with the Ansible Galaxy CLI:

    ansible-galaxy collection install git+https://github.com/mihaTrajbaric/k8s.git

You can also include it in a `requirements.yml` file and install it via `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: https://github.com/mihaTrajbaric/k8s.git
    type: git
```


### Installing the Collection from Ansible Galaxy (TODO - no published yet)

Before using the Sodalite.8s collection, you need to install it with the Ansible Galaxy CLI:

    ansible-galaxy collection install sodalite.k8s

You can also include it in a `requirements.yml` file and install it via `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: sodalite.k8s
    version: 1.0.0
```

### Installing the Kubernetes Python Library

Content in this collection requires the [Kubernetes Python client](https://pypi.org/project/kubernetes/) to interact with Kubernetes' APIs. You can install it with:

    pip3 install kubernetes>=12.0.0

### Using modules from the Kubernetes Collection in your playbooks

It's preferable to use content in this collection using their Fully Qualified Collection Namespace (FQCN), for example `sodalite.k8s.deployment`:

```yaml
---
- hosts: localhost
  gather_facts: false
  connection: local

  tasks:
    - name: Ensure namespace exists.
      sodalite.k8s.namespace:
        name: test-namespace
        state: present

    - name: Create new configmap
      sodalite.k8s.config_map:
        name: myapp-config
        namespace: test-namespace
        data:
          DB_IP: another-service

    - name: Ensure the myapp Deployment exists
      sodalite.k8s.deployment:
        name: myapp-deployment
        namespace: test-namespace
        state: present
        labels:
          app: myapp
        selector:
          match_labels:
            app: myapp
        containers:
          - name: myapp-container
            image: myapp:latest
            ports:
              - host_port: 80
                container_port: 80
                protocol: TCP
            env_from:
              - config_map:
                  name: myapp-config

    - name: Ensure the myapp Service exists
      sodalite.k8s.service:
        name: myapp-service
        namespace: test-namespace
        state: present
        type: LoadBalancer
        selector:
          app: myapp
        ports:
          - name: my-port
            port: 8080
            target_port: 8080
```

See [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## Contributing to this collection (TODO)

<!--Describe how the community can contribute to your collection. At a minimum, include how and where users can create issues to report problems or request features for this collection.  List contribution requirements, including preferred workflows and necessary testing, so you can benefit from community PRs. If you are following general Ansible contributor guidelines, you can link to - [Ansible Community Guide](https://docs.ansible.com/ansible/latest/community/index.html). -->


## Release notes

See the [changelog](https://github.com/mihaTrajbaric/k8s/tree/main/CHANGELOG.rst).

<!-- ## Roadmap -->

<!-- Optional. Include the roadmap for this collection, and the proposed release/versioning strategy so users can anticipate the upgrade/update cycle. -->

## Licensing

<!-- Include the appropriate license information here and a pointer to the full licensing details. If the collection contains modules migrated from the ansible/ansible repo, you must use the same license that existed in the ansible/ansible repo. See the GNU license example below. -->

GNU General Public License v3.0 or later.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.

