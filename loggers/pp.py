import json
def prettyPrintJson(ugly_json):
    parsed_json = json.loads(ugly_json)
    pretty_json = json.dumps(parsed_json, indent=2)

    print(pretty_json)