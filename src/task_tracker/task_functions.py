import argparse
from datetime import date, datetime
from enum import Enum
from pathlib import Path
import os
import json


FILE_PATH = Path.cwd() / "task_cli.json"

class TaskError(Exception):
    pass

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

def generate_id() -> int:
    with open(FILE_PATH, 'r', encoding='UTF-8') as f:
        data = json.load(f)
    return max((task["id"] for task in data["tasks"]), default=0) + 1

def load_tasks() -> list[dict]:
    if not os.path.exists(FILE_PATH):
        return []
    else:
        with open(FILE_PATH, encoding='UTF-8') as f:
            return json.load(f).get("tasks", [])

def save_tasks(tasks: list[dict]) -> None:
    with open(FILE_PATH, 'w', encoding='UTF-8') as f:
        json.dump({"tasks": tasks}, f, indent=4) 

def add(description: str, status: Status) -> str:
    new_id = 1
    current_date = datetime.now().isoformat()

    if description.strip():
        new_task = {"id": new_id, "description": description, "status": status.value, "createdAt": current_date, "updatedAt": current_date}
    else:
        raise TaskError("Task description cannot be empty.")
    
    if not os.path.exists(FILE_PATH):
        json_content = {"tasks": [new_task]}
        with open(FILE_PATH, 'x', encoding='UTF-8') as f:
            json.dump(json_content, f, indent=4)
    else:
        data = load_tasks()
        new_id = generate_id()
        new_task["id"] = new_id
        data.append(new_task)
        save_tasks(data)
    return f"You have added a new task with id {new_id}."

def update(id: int, description: str) -> str:
    data = load_tasks()
    task_found = False
    for task in data:
        if task["id"] == id:
            if description != task["description"]:
                task["description"] = description
                task["updatedAt"] = datetime.now().isoformat()
                task_found = True
                break
            else:
                raise TaskError("There are no changes detected in the description. Update unsuccessful.")

    if not task_found:
        raise TaskError(f"Task with id {id} not found.")

    save_tasks(data)
    return f"Task {id} updated successfully."

def delete(id: int) -> str:
    tasks = load_tasks()
    updated_tasks = [task for task in tasks if task["id"] != id]

    if len(tasks) == len(updated_tasks):
        raise TaskError(f"Task with id {id} not found.")

    tasks = updated_tasks
    save_tasks(tasks)

    return f"Task {id} successfully deleted."

def list_tasks(status: Status) -> str:
    data = load_tasks()

    if len(data) == 0:
        raise TaskError("No tasks have been found.")
    
    if status:
        for item in data:
            if item["status"] == status.value:
                print(f"[{item['id']}] {item["status"]}: {item['description']}")
    else:
        for item in data:
            print(f"[{item['id']}] {item["status"]}: {item['description']}")
    return "All the tasks have been listed."

def set_status(id: int, status: Status) -> str:
    marked = False
    data = load_tasks()
    for item in data:
        if item["id"] == id:
            if item["status"] != status.value:
                item["status"] = status.value
                item["updatedAt"] = datetime.now().isoformat()
                marked = True
                break
            else:
                raise TaskError(f"Task {id} already has status {status.value}.")
    if marked:
        save_tasks(data)
        return f"Task with {id} marked as {status.value}."
    else:
        raise TaskError(f"Task with id {id} not found.")

def mark_in_progress(id: int) -> str:
    return set_status(id, Status.IN_PROGRESS)

def mark_done(id: int) -> str:
    return set_status(id, Status.DONE)

def mark_todo(id: int) -> str:
    return set_status(id, Status.TODO)