import dataclasses, datetime, json

# Deserialize sample
#   bill_dict = json.loads(bill_json)
#   bill = json_util.dataclass_from_dict(eb.ElectricityBill, bill_dict)

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)
        elif isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        else:
            return super().default(obj)

def dataclass_from_dict(class_type, d):
    try:
        fieldtypes = {f.name:f.type for f in dataclasses.fields(class_type)}
        return class_type(**{f:dataclass_from_dict(fieldtypes[f],d[f]) for f in d})
    except:
        return d # Not a dataclass field
