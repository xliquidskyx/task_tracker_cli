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
def add(description: str, status: str) -> None:
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

def update(id: int, new_description=None, new_status=None) -> str:
    if not os.path.exists(file_path):
        return "Error: No tasks file found."
    
    with open(file_path, 'r') as f:
        data = json.load(f)

    task_found = False
    for task in data.get("tasks", []):
        if task["id"] == int(id):
            if new_description:
                task["description"] = new_description
            if new_status:
                task["status"] = new_status
            task["updated_at"] = current_date.isoformat()
            task_found = True
            break

    if not task_found:
        return f"Error: Task with id: {id} not found."

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4, default=json_serial)

    return f"Task {id} updated successfully."


def delete(id: int):
    return 0

def list_tasks() -> str:
    with open(file_path, 'r') as f:
        data = json.load(f)
        for item in data["tasks"]:
            print(item)
    return ""

global_parser = argparse.ArgumentParser(prog="task_cli")
subparsers = global_parser.add_subparsers(
    title="subcommands", help="task management commands", dest="command"
)

add_parser = subparsers.add_parser("add", help="Add new task to a JSON file")
add_parser.add_argument("description", type=str, help="The task description")
add_parser.add_argument("status", type=str, nargs="?", default="todo", help="The initial status")
add_parser.set_defaults(func=add)

update_parser = subparsers.add_parser("update", help="Update an existing task.")
update_parser.add_argument("id", type=int, help="Id of the task.")
update_parser.add_argument("-d", "--description", type=str, default=None, metavar="TEXT", help="New task description.")
update_parser.add_argument("-s", "--status", type=str, default=None, metavar="STATUS", help="New task status.")
update_parser.set_defaults(func=update)

list_parser = subparsers.add_parser("list", help="List all JSON tasks.")
list_parser.set_defaults(func=list_tasks)

args = global_parser.parse_args()

if args.command == "add":
    print(args.func(args.description, args.status))
elif args.command == "update":
    print(args.func(args.id, args.description, args.status))
elif args.command == "list":
    print(args.func())
else:
    global_parser.print_help()