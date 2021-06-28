from __future__ import absolute_import, division, print_function
from kubernetes import config, dynamic
from kubernetes.client import api_client, exceptions
from kubernetes.dynamic.exceptions import (
        NotFoundError, ResourceNotFoundError, ResourceNotUniqueError, DynamicApiError,
        ConflictError, ForbiddenError, MethodNotAllowedError, BadRequestError,
        KubernetesValidateMissing
    )
import base64
import urllib3
from ansible.module_utils.basic import AnsibleModule


# TODO Import checking
# TODO configuration

def get_api_client(module: AnsibleModule):
    # TODO expand api client options
    dyn_client = dynamic.DynamicClient(
        api_client.ApiClient(configuration=config.load_kube_config())
    )
    return dyn_client

class Base64:

    # TODO can also be done with ansible

    @staticmethod
    def encode(message: str) -> str:
        return base64.b64encode(message.encode('ascii')).decode('ascii')

    @staticmethod
    def decode(message: str) -> str:
        return base64.b64decode(message.encode('ascii')).decode('ascii')


class K8s:

    def __init__(self, module: AnsibleModule, body: dict):
        self.client = None
        self.module = module
        self.check_mode = self.module.check_mode
        self.argspec = self.module.argument_spec
        self.params = self.module.params
        self.exit_json = self.module.exit_json
        self.fail_json = self.module.fail_json

        self.state = self.module.params.get('state')
        self.name = self.module.params.get('name')
        self.namespace = self.module.params.get('namespace')
        self.force = self.module.params.get('force')
        self.apply = self.module.params.get('apply')
        self.body = body
        self.api_version = body.get('apiVersion')
        self.kind = body.get('kind')

    def execute_module(self):
        changed = False
        result = None

        try:
            self.client = get_api_client(self.module)

        except urllib3.exceptions.RequestError as e:
            self.fail_json(msg="Couldn't connect to Kubernetes: %s" % str(e))

        # TODO some error handling
        # TODO check_mode
        # TODO return values

        if self.state == 'present':
            result, changed = self.present()
        else:
            result, changed = self.absent()

        self.exit_json(**{
            'changed': changed,
            'result': result
        })

    # check if old has any new keys
    def object_diff(self, old_object: dict, new_object: dict):
        different = False
        for key, value_new in new_object.items():
            try:
                value_old = old_object[key]
            except KeyError:
                return True
            if isinstance(value_new, dict) and isinstance(value_old, dict):
                different = different or self.object_diff(value_old, value_new)
            else:
                different = different or (value_new != value_old)
        return different

    def present(self):
        api = self.client.resources.get(api_version=self.api_version, kind=self.kind)

        try:
            body_new = api.create(body=self.body, namespace=self.namespace)
            return body_new.to_dict(), True
        except ConflictError as e:

            if self.force:
                body_forced = api.replace(
                    name=self.name, namespace=self.namespace, body=self.body
                )
                return body_forced.to_dict(), True

            if self.apply:

                body_old = api.get(name=self.name, namespace=self.namespace)
                if not self.object_diff(body_old.to_dict(), self.body):
                    return body_old.to_dict(), False

                # replace or patch?
                body_applied = api.replace(
                    name=self.name, namespace=self.namespace, body=self.body
                )
                return body_applied.to_dict(), True

            return None, False

    def absent(self):
        api = self.client.resources.get(api_version=self.api_version, kind=self.kind)
        try:
            response = api.delete(name=self.name, namespace=self.namespace)
            return response.to_dict(), True
        except NotFoundError:
            return None, False
