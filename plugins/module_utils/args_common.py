from __future__ import (absolute_import, division, print_function)
from ansible_collections.kubernetes.core.plugins.module_utils.args_common import (
    AUTH_ARG_SPEC, WAIT_ARG_SPEC, DELETE_OPTS_ARG_SPEC)

import copy

__metaclass__ = type

COMMON_ARG_SPEC = dict(
    state=dict(
        default='present',
        choices=['present', 'absent', 'patched']
    ),
    name=dict(
        type='str',
        required=True
    ),
    namespace=dict(
        type='str',
        default='default'
    ),
    force=dict(
        type='bool',
        default=False
    ),
    merge_type=dict(
        type='list',
        elements='str',
        choices=['json', 'merge', 'strategic-merge']
    ),
    validate=dict(
        type='dict',
        default=None,
        options=dict(
            fail_on_error=dict(type='bool'),
            version=dict(),
            strict=dict(type='bool', default=True)
        )
    ),
    append_hash=dict(
        type='bool',
        default=False
    ),
    apply=dict(
        type='bool',
        default=False
    )

)


METADATA_ARG_SPEC = dict(
    metadata=dict(
        type='dict',
        default={},
        options=dict(
            labels=dict(type='dict'),
            annotations=dict(type='dict')
        )
    )
)


def common_arg_spec():
    argument_spec = copy.deepcopy(COMMON_ARG_SPEC)
    argument_spec.update(copy.deepcopy(AUTH_ARG_SPEC))
    argument_spec.update(copy.deepcopy(WAIT_ARG_SPEC))
    argument_spec.update(copy.deepcopy(METADATA_ARG_SPEC))
    argument_spec['delete_options'] = dict(type='dict', default=None, options=copy.deepcopy(DELETE_OPTS_ARG_SPEC))
    return argument_spec


COMMON_MUTALLY_EXCLUSIVE = [
    ('merge_type', 'apply')
]

COMMON_RETURN = r'''
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
       type: complex
     spec:
       description: Specific attributes of the object.
       returned: success
       type: complex
     status:
       description: Current status details for the object.
       returned: success
       type: complex
     duration:
       description: elapsed time of task in seconds
       returned: when C(wait) is true
       type: int
       sample: 48
     error:
       description: error while trying to create/delete the object.
       returned: error
       type: complex
'''
