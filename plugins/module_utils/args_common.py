from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

COMMON_ARG_SPEC = {
    'state': {
        'default': 'present',
        'choices': ['present', 'absent'],
    },
    'name': {
        'type': 'str',
        'required': True
    },
    'namespace': {
        'type': 'str',
        'default': 'default'
    },
    'force': {
        'type': 'bool',
        'default': False,
    }
}
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
