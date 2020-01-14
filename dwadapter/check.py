KEY_TYPE_STR = ['str']

TAG_VALUE_TYPE_STR = ['str']

FIELD_VALUE_TYPE_STR = ['str', 'int', 'float', 'bool']

def CheckMeasurement(measurement):
    return type(measurement).__name__ == 'str'

def CheckTags(tags):
    # tags可以为空
    if not tags:
        return True

    if not isinstance(tags, dict):
        return False

    ks = [type(k).__name__ for k in tags.keys()]
    key_valid =all([i in KEY_TYPE_STR for i in ks])

    vs = [type(v).__name__ for v in tags.values()]
    val_valid = all([i in TAG_VALUE_TYPE_STR for i in vs])

    return  key_valid and val_valid

def CheckFields(fields):
    # fileds必须非空
    if not fields:
        return False

    if not isinstance(fields, dict):
        return False

    ks = [type(k).__name__ for k in fields.keys()]
    key_valid = all([i in KEY_TYPE_STR for i in  ks])

    vs = [type(v).__name__ for v in fields.values()]
    val_valid = all([i in FIELD_VALUE_TYPE_STR for i in vs])

    return key_valid and val_valid

def CheckTagsAndFields(tags, fields):
    return CheckTags(tags) and CheckFields(fields)

def CheckTimestamp(timestamp):
    return type(timestamp).__name__ == 'int'

def CheckMetrics(measurement, tags, fields, timestamp):
    return CheckMeasurement(measurement) and CheckTagsAndFields(tags, fields) and CheckTimestamp(timestamp)