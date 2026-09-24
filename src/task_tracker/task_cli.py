import argparse
from datetime import date, datetime
import os
import json


file_path = "task_cli.json"
current_date = datetime.now()

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))


#TODO: status as enum
def add(description: str, status: str):
    new_task = {"id": 2, "description": description, "status": status, "created_at": current_date, "updated_at": current_date}

    if not os.path.exists(file_path):
        json_content = {"tasks": [new_task]}
        with open(file_path, 'x') as f:
            json.dump(json_content, f, indent=4, default=json_serial)
    else:
       with open(file_path, 'r+') as f:
           data = json.load(f)
           data["tasks"].append(new_task)
           f.seek(0)
           json.dump(data, f, indent=4, default=json_serial)

    return "You have added a new task with ID X."

def update(id: int, description: str, status: str):
    return 0

def delete(id: int):
    return 0

def list() -> str:
    with open(file_path, 'r') as f:
        data = json.load(f)
        for item in data:
            print(item)


global_parser = argparse.ArgumentParser(prog="task_cli")
subparsers = global_parser.add_subparsers(
    title="subcommands", help="task management commands", dest="command"
)
arg_template = {
    "dest": "operands",
    "type": str,
    "nargs": '?',
    "metavar": "OPERAND",
    "help": "a string value",
}

add_parser = subparsers.add_parser("add", help="Add new task to a JSON file")
add_parser.add_argument(**arg_template)
add_parser.set_defaults(func=add)

list_parser = subparsers.add_parser("list", help="List all JSON tasks.")
list_parser.set_defaults(func=list)

args = global_parser.parse_args()

if args.command == "add":
    print(args.func(args.description, args.status))
elif args.command == "list":
    print(args.func())
else:
    global_parser.print_help()