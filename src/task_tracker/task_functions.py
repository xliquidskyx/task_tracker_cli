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

    try:
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
    
    except Exception:
        raise Exception("Couldn't add a new task. Please try again.")

def update(id: int, new_description=None, new_status=None) -> str:
    try:
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

    except Exception:
        raise Exception("Couldn't update the task. Please, try again.")


def delete(id: int) -> str:
    try:
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

    except Exception:
        raise Exception("Couldn't delete the task. Please, try again.")

def list_tasks(status: Status) -> str:
    try:
        if not os.path.exists(file_path):
            return "Error: File path not found."
        
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
        return "All the tasks have been listed."

    except Exception:
        raise Exception("We couldn't list the tasks. Please, try again.")

def mark_in_progress(id: int) -> str:
    try:
        if not os.path.exists(file_path):
            return "Error: File path not found."

        marked = False

        with open(file_path, 'r+') as f:
            data = json.load(f)
            if id:
                for item in data["tasks"]:
                    if item["id"] == int(id):
                        item["status"] = "in-progress"
                        item["updated_at"] = current_date
                        marked = True
                    else:
                        continue

        if marked:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4, default=json_serial)
            return f"Task with id: {id} successfully marked as in progress."
        else:
            return f"Task with id: {id} not found."

    except Exception:
        raise Exception("We couldn't mark the task as in progress. Please, try again.")

def mark_done(id: int) -> str:
    try:
        if not os.path.exists:
            return "Error: File not found"

        marked = False

        with open(file_path, 'r+') as f:
            data = json.load(f)
            if id:
                for item in data["tasks"]:
                    if item["id"] == int(id):
                        item["status"] = "done"
                        item["updated_at"] = current_date
                        marked = True
                    else:
                        continue

        if marked:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4, default=json_serial)
            return f"Task with id: {id} successfuly marked as done."
        else:
            return f"Task with id: {id} not found."

    except Exception:
        raise Exception("We couldn't mark the task as done. Please, try again.")
