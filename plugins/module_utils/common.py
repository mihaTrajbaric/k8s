from __future__ import absolute_import, division, print_function
__metaclass__ = type

import base64

K8S_IMP_ERR = None
try:
    from kubernetes import config, dynamic
    from kubernetes.client import api_client, exceptions
    from kubernetes.dynamic.exceptions import (
        NotFoundError, ResourceNotFoundError, ResourceNotUniqueError, DynamicApiError,
        ConflictError, ForbiddenError, MethodNotAllowedError, BadRequestError,
        KubernetesValidateMissing
    )
    HAS_K8S_MODULE_HELPER = True
    k8s_import_exception = None
except ImportError as e:
    HAS_K8S_MODULE_HELPER = False
    k8s_import_exception = e

try:
    import urllib3
    urllib3.disable_warnings()
except ImportError:
    pass


# TODO Import checking
# TODO configuration

def get_api_client(module):
    # TODO expand api client options
    dyn_client = dynamic.DynamicClient(
        api_client.ApiClient(configuration=config.load_kube_config())
    )
    return dyn_client


class Base64:

    # TODO can it also be done with ansible?

    @staticmethod
    def encode(message):
        return base64.b64encode(message.encode('ascii')).decode('ascii')

    @staticmethod
    def decode(message):
        return base64.b64decode(message.encode('ascii')).decode('ascii')

    @staticmethod
    def validate(message):
        try:
            return Base64.encode(Base64.decode(message)) == message
        except Exception:
            return False


class Result:
    api_version = None
    kind = None
    spec = None
    status = None
    error = None
    metadata = None
    # duration = None


class K8s:

    def __init__(self, module, definition):
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
        self.definition = definition
        self.api_version = self.definition.get('apiVersion')
        self.kind = self.definition.get('kind')
        self.metadata = self.definition.get('metadata')

        self.resource = None

    def find_resource(self, fail=False):
        for attribute in ['kind', 'name', 'singular_name']:
            try:
                return self.client.resources.get(**{'api_version': self.api_version, attribute: self.kind})
            except (ResourceNotFoundError, ResourceNotUniqueError):
                pass
        try:
            return self.client.resources.get(api_version=self.api_version, kind=self.kind)
        except (ResourceNotFoundError, ResourceNotUniqueError):
            if fail:
                self.fail_json(msg='Failed to find exact match for {0}.{1} by [kind, name, singularName, shortNames]'.format(
                    self.api_version, self.kind))

    def execute_module(self):
        changed = False
        result = None
        existing = None

        try:
            self.client = get_api_client(self.module)

        except urllib3.exceptions.RequestError as e:
            self.fail_json(msg="Couldn't connect to Kubernetes: %s" % str(e))

        self.resource = self.find_resource(fail=True)

        try:
            existing = self.resource.get(name=self.name, namespace=self.namespace)
        except NotFoundError:
            pass
        except (DynamicApiError, ForbiddenError) as e:
            self.fail_json(msg='Failed to retrieve requested object: {0}'.format(e.body), error=e.status, status=e.status, reason=e.reason)

        if self.state == 'absent':
            if not existing:
                pass
            else:
                changed = True
                if not self.check_mode:
                    try:
                        self.resource.delete(name=self.name, namespace=self.namespace)
                    except DynamicApiError as e:
                        self.fail_json(msg="Failed to delete object: {0}".format(e.body), error=e.status,
                                       status=e.status, reason=e.reason)
        else:
            # state present
            if not existing:
                changed = True
                if not self.check_mode:
                    try:
                        result = self.resource.create(body=self.definition, namespace=self.namespace).to_dict()
                    except DynamicApiError as e:
                        self.fail_json(msg="Failed to create object: {0}".format(e.body), error=e.status,
                                       status=e.status, reason=e.reason)
                else:
                    result = self.definition
            else:
                if self.force:
                    changed = True
                    if not self.check_mode:
                        try:
                            result = self.resource.replace(
                                name=self.name, namespace=self.namespace, body=self.definition
                            ).to_dict()
                        except DynamicApiError as e:
                            self.fail_json(msg="Failed to replace object: {0}".format(e.body), error=e.status,
                                           status=e.status, reason=e.reason)
                    else:
                        result = self.definition
                else:
                    if not self.object_diff(existing.to_dict(), self.definition):
                        result = existing.to_dict()
                    else:
                        changed = True
                        if not self.check_mode:
                            try:
                                result = self.resource.patch(
                                    name=self.name, namespace=self.namespace, body=self.definition
                                ).to_dict()
                            except DynamicApiError as e:
                                self.fail_json(msg="Failed to patch object: {0}".format(e.body), error=e.status,
                                               status=e.status, reason=e.reason)
                        else:
                            # TODO return how patched object would look like
                            pass
        # TODO wait

        self.exit_json(**{
            'changed': changed,
            'result': result
        })

    # check if old has any new keys
    def object_diff(self, old_object, new_object):
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
