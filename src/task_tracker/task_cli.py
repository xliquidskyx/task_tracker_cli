import argparse
from datetime import date, datetime
from enum import Enum
import os
import json


file_path = "task_cli.json"
current_date = datetime.now()

class Status(Enum):
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"

    @classmethod
    def from_string(cls, value: str):
        # Normalize text to lowercase and replace underscores with dashes
        normalized = value.strip().lower().replace("_", "-")
        for item in cls:
            if item.value == normalized:
                return item
        raise argparse.ArgumentTypeError(f"Invalid status value: '{value}'. Choose from: todo, in-progress, done")
    
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def generate_id(data) -> None:
    for i, task in enumerate(data.get("tasks", [])):
        task["id"] = i + 1
    return None

def add(description: str, status: Status) -> None:
    new_task = {"id": 1, "description": description, "status": status.value, "created_at": current_date, "updated_at": current_date}

    if not os.path.exists(file_path):
        json_content = {"tasks": [new_task]}
        with open(file_path, 'x') as f:
            json.dump(json_content, f, indent=4, default=json_serial)
    else:
       with open(file_path, 'r+') as f:
           data = json.load(f)
           data["tasks"].append(new_task)
           f.seek(0)
           generate_id(data)
           json.dump(data, f, indent=4, default=json_serial)

    return "You have added a new task."

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
                task["status"] = new_status.value
            task["updated_at"] = current_date.isoformat()
            task_found = True
            break

    if not task_found:
        return f"Error: Task with id: {id} not found."

    generate_id(data)

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4, default=json_serial)

    return f"Task {id} updated successfully."


def delete(id: int) -> str:
    if not os.path.exists(file_path):
        return "Error: File path not found."
    
    with open(file_path, 'r') as f:
        data = json.load(f)

    tasks = data.get("tasks", [])
    updated_tasks = [task for task in tasks if task["id"] != int(id)]

    if len(tasks) == len(updated_tasks):
        return f"Error: Task with id: {id} not found."

    data["tasks"] = updated_tasks
    generate_id(data)

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4, default=json_serial)

    return f"Task {id} successfully deleted."

def list_tasks(status: Status) -> str:
    with open(file_path, 'r') as f:
        data = json.load(f)
        if status:
            for item in data["tasks"]:
                if item["status"] == status.value:
                    print(item)
                else:
                    continue
        else:
            for item in data["tasks"]:
                print(item)
    return ""

global_parser = argparse.ArgumentParser(prog="task_cli")
subparsers = global_parser.add_subparsers(
    title="subcommands", help="task management commands", dest="command"
)

add_parser = subparsers.add_parser("add", help="Add new task to a JSON file")
add_parser.add_argument("description", type=str, help="The task description")
add_parser.add_argument("status", type=Status.from_string, nargs="?", default="todo", help="The initial status")
add_parser.set_defaults(func=add)

update_parser = subparsers.add_parser("update", help="Update an existing task.")
update_parser.add_argument("id", type=int, help="Id of the task.")
update_parser.add_argument("-d", "--description", type=str, default=None, metavar="TEXT", help="New task description.")
update_parser.add_argument("-s", "--status", type=Status.from_string, default=None, metavar="STATUS", help="New task status.")
update_parser.set_defaults(func=update)

delete_parser = subparsers.add_parser("delete", help="Delete a task.")
delete_parser.add_argument("id", type=int, help="Id of the task.")
delete_parser.set_defaults(func=delete)

list_parser = subparsers.add_parser("list", help="List all JSON tasks.")
list_parser.add_argument("-s", "--status", type=Status.from_string, default=None, metavar="STATUS", help="List tasks with given status.")
list_parser.set_defaults(func=list_tasks)

args = global_parser.parse_args()

if args.command == "add":
    print(args.func(args.description, args.status))
elif args.command == "update":
    print(args.func(args.id, args.description, args.status))
elif args.command == "delete":
    print(args.func(args.id))
elif args.command == "list":
    print(args.func(args.status))
else:
    global_parser.print_help()