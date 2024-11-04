import json


def _default(val):  # noqa: ANN202, ANN001
    if isinstance(val, set):
        return list(val)
    return json.JSONEncoder().default(val)


def dumps(d):  # noqa: ANN201, ANN001
    return json.dumps(d, default=_default)
