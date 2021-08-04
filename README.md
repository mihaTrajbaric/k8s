# SODALITE Kubernetes (k8s) collection
<!-- Add CI and code coverage badges here. Samples included below. -->
[![CI](https://github.com/ansible-collections/REPONAMEHERE/workflows/CI/badge.svg?event=push)](https://github.com/ansible-collections/REPONAMEHERE/actions) [![Codecov](https://img.shields.io/codecov/c/github/ansible-collections/REPONAMEHERE)](https://codecov.io/gh/ansible-collections/REPONAMEHERE)

<!-- Describe the collection and why a user would want to use it. What does the collection do? -->

## Tested with Ansible

<!--start requires_ansible-->
## Ansible version compatibility

This collection has been tested against following Ansible versions: **>=2.9.10**.

Plugins and modules within a collection may be tested with only specific Ansible versions.
A collection may contain metadata that identifies these versions.
PEP440 is the schema used to describe the versions of Ansible.
<!--end requires_ansible-->

## External requirements

<!-- List any external resources the collection depends on, for example minimum versions of an OS, libraries, or utilities. Do not list other Ansible collections here. -->

### Supported connections
<!-- Optional. If your collection supports only specific connection types (such as HTTPAPI, netconf, or others), list them here. -->

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

<!-- Galaxy will eventually list the module docs within the UI, but until that is ready, you may need to either describe your plugins etc here, or point to an external docsite to cover that information. -->

## Using this collection

<!--Include some quick examples that cover the most common use cases for your collection content. -->

See [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## Contributing to this collection

<!--Describe how the community can contribute to your collection. At a minimum, include how and where users can create issues to report problems or request features for this collection.  List contribution requirements, including preferred workflows and necessary testing, so you can benefit from community PRs. If you are following general Ansible contributor guidelines, you can link to - [Ansible Community Guide](https://docs.ansible.com/ansible/latest/community/index.html). -->


## Release notes

See the [changelog](https://github.com/ansible-collections/REPONAMEHERE/tree/main/CHANGELOG.rst).

## Roadmap

<!-- Optional. Include the roadmap for this collection, and the proposed release/versioning strategy so users can anticipate the upgrade/update cycle. -->

## More information

<!-- List out where the user can find additional information, such as working group meeting times, slack/IRC channels, or documentation for the product this collection automates. At a minimum, link to: -->

- [Ansible Collection overview](https://github.com/ansible-collections/overview)
- [Ansible User guide](https://docs.ansible.com/ansible/latest/user_guide/index.html)
- [Ansible Developer guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html)
- [Ansible Collections Checklist](https://github.com/ansible-collections/overview/blob/master/collection_requirements.rst)
- [Ansible Community code of conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)
- [The Bullhorn (the Ansible Contributor newsletter)](https://us19.campaign-archive.com/home/?u=56d874e027110e35dea0e03c1&id=d6635f5420)
- [Changes impacting Contributors](https://github.com/ansible-collections/overview/issues/45)

## Licensing

<!-- Include the appropriate license information here and a pointer to the full licensing details. If the collection contains modules migrated from the ansible/ansible repo, you must use the same license that existed in the ansible/ansible repo. See the GNU license example below. -->

GNU General Public License v3.0 or later.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.

