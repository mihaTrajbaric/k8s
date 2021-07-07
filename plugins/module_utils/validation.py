from __future__ import absolute_import, division, print_function
__metaclass__ = type

import base64
import re


class Base64:

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


class Validators:

    @staticmethod
    def alphanumeric(value):
        """
        validates that value consist only of alphanumeric characters, '-', '_' or '.'.
        """
        regex = re.compile(r'^[a-zA-Z0-9_.-]+$')
        return bool(regex.match(str(value)))

    @staticmethod
    def string_string_dict(_dict):
        """
        Ensures all keys and values are strings
        """
        if _dict is None:
            return True
        return all([isinstance(value, str) and isinstance(key, str) for key, value in _dict.items()])

    @staticmethod
    def string_byte_dict(_dict):
        """
        Ensures all keys are strings and all values are base64
        """
        if _dict is None:
            return True
        return all([isinstance(value, str) and Validators.base64(value) for key, value in _dict.items()])

    @staticmethod
    def base64(message):
        return Base64.validate(message)
