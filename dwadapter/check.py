from collections import OrderedDict

def check_measurement(measurement):
    return isinstance(measurement, str)

def check_tags(tags):
    # tags可以为空
    if not tags:
        return True

    if not isinstance(tags, dict) and not isinstance(tags, OrderedDict):
        return False

    ks = [isinstance(k, str) for k in tags.keys()]
    key_valid = all(ks)

    vs = [isinstance(v, str) for v in tags.values()]
    val_valid = all(ks)

    return  key_valid and val_valid

def check_fields(fields):
    # fileds必须非空
    if not fields:
        return False

    if not isinstance(fields, dict) and not isinstance(fields, OrderedDict):
        return False

    ks = [isinstance(k, str) for k in fields.keys()]
    key_valid = all(ks)

    vs = [isinstance(v, (str, int, float, bool)) for v in fields.values()]
    val_valid = all(vs)

    return key_valid and val_valid

def check_tags_fields(tags, fields):
    return check_tags(tags) and check_fields(fields)

def check_timestamp(timestamp):
    return isinstance(timestamp, int)

def check_metrics(measurement, tags, fields, timestamp):
    return check_measurement(measurement) and check_tags_fields(tags, fields) and check_timestamp(timestamp)