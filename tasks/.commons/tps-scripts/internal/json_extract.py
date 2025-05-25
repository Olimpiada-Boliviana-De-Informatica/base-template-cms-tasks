import sys
import os

from util import load_json, write_exception_messages, value_to_bash_str_ln


def navigate_json(data, path, json_file_name):
    for part in path.split('/'):
        if part == '.':
            continue
        try:
            if isinstance(data, dict):
                data = data[part]
            elif isinstance(data, list):
                data = data[int(part)]
            else:
                raise LookupError(
                    "Reaching null data"
                    if data is None else
                    ("Reaching data of type '{}'".format(type(data).__name__))
                )
        except Exception as exc:
            raise Exception(
                "Requested key '%s' not found in '%s'" % (path, os.path.basename(json_file_name))
            ) from exc
    return data


def navigate_json_file(file, path):
    return navigate_json(load_json(file), path, file)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        from util import simple_usage_message
        simple_usage_message("<json-file> <json-path>")

    json_file = sys.argv[1]
    json_path = sys.argv[2]

    try:
        result = navigate_json_file(json_file, json_path)
    except Exception as exc:
        write_exception_messages(exc)
        sys.exit(4)

    sys.stdout.write(value_to_bash_str_ln(result))
