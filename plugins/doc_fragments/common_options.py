from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    DOCUMENTATION = r'''
options:
    state:
        description:
        - Determines if an object should be created, or deleted. When set to C(present), an object will be
          created, if it does not already exist. If set to C(absent), an existing object will be deleted. If set to
          C(present), an existing object will be patched, if its attributes differ from those specified as module params.
        type: str
        default: present
        choices: [ absent, patched, present ]
    name:
        description:
        - Use to specify an object name.
        - Use to create, delete, or discover an object without providing a full resource definition.
        - Use in conjunction with I(namespace) to identify a specific object.
        type: str
        required: True
    namespace:
        description:
        - Use to specify an object namespace.
        - Use in conjunction with I(name) to identify a specific object.
        type: str
        default: default
requirements:
  - "python >= 3.6"
  - "kubernetes >= 12.0.0"
  - "PyYAML >= 3.11"
  - "jsonpatch"
'''
