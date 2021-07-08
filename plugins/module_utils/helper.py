from __future__ import absolute_import, division, print_function
__metaclass__ = type


def clean_dict(d):
    """
    Removes all keys, that do not have any real data.
    """
    if isinstance(d, dict):
        cleaned_recursively = {k: clean_dict(v) for k, v in d.items()}
        cleaned = {k: v for k, v in cleaned_recursively.items() if v is not None}
        if len(cleaned) == 0:
            return None
        return cleaned
    if isinstance(d, list):
        cleaned_recursively = [clean_dict(item) for item in d]
        cleaned = [item for item in cleaned_recursively if item is not None]
        if len(cleaned) == 0:
            return None
        return cleaned

    return d
