from datetime import datetime
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
        raise ValueError(f"Invalid status value: '{value}'. Choose from: todo, in-progress, done")

def load_tasks() -> list[dict]:
    """Loads objects (tasks) from a JSON file."""
    if not os.path.exists(FILE_PATH):
        return []
    
    with open(FILE_PATH, encoding='UTF-8') as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise TaskError("Task file has invalid format.")

    tasks = data.get("tasks", [])
    if not (isinstance(tasks, list) and all(isinstance(task, dict) for task in tasks)):
        raise TaskError("Task file has invalid format.")

    return tasks

def save_tasks(tasks: list[dict]) -> None:
    """Saves list of objects (tasks) into a JSON file."""
    with open(FILE_PATH, 'w', encoding='UTF-8') as f:
        json.dump({"tasks": tasks}, f, indent=4)

def is_empty(description: str) -> bool:
    """Returns true if given string (description) is empty."""
    return not description.strip()

def add(description: str, status: Status) -> str:
    """Creates a new JSON file if does not exist and appends a new task into it."""
    current_date = datetime.now().isoformat()
    empty_description = is_empty(description)

    if empty_description:
        raise TaskError("Task description cannot be empty.")

    tasks = load_tasks()
    new_id = max((task["id"] for task in tasks), default=0) + 1
    new_task = {"id": new_id, "description": description, "status": status.value, "createdAt": current_date, "updatedAt": current_date}
    tasks.append(new_task)
    save_tasks(tasks)
    return f"You have added a new task with id {new_id}."

def update(task_id: int, description: str) -> str:
    """Updates a description of a task with given ID."""
    data = load_tasks()
    task_found = False
    empty_description = is_empty(description)

    if empty_description:
        raise TaskError("Task description cannot be empty.")
    
    for task in data:
        if task["id"] == task_id:
            if description != task["description"]:
                task["description"] = description
                task["updatedAt"] = datetime.now().isoformat()
                task_found = True
                break
            else:
                raise TaskError("There are no changes detected in the description. Update unsuccessful.")

    if not task_found:
        raise TaskError(f"Task with id {task_id} not found.")

    save_tasks(data)
    return f"Task {task_id} updated successfully."

def delete(task_id: int) -> str:
    """Deletes task with given ID."""
    tasks = load_tasks()
    updated_tasks = [task for task in tasks if task["id"] != task_id]

    if len(tasks) == len(updated_tasks):
        raise TaskError(f"Task with id {task_id} not found.")

    save_tasks(updated_tasks)

    return f"Task {task_id} successfully deleted."

def list_tasks(status: Status | None) -> list[str]:
    """Lists all tasks or lists tasks with given status if provided."""
    tasks = load_tasks()
    if status:
        tasks = [task for task in tasks if task["status"] == status.value]
    if not tasks:
        raise TaskError("No tasks have been found.")
    return [f"[{task['id']}] {task['status']}: {task['description']}" for task in tasks]

def set_status(task_id: int, status: Status) -> str:
    """Changes status of a task with given ID."""
    marked = False
    data = load_tasks()
    for item in data:
        if item["id"] == task_id:
            if item["status"] != status.value:
                item["status"] = status.value
                item["updatedAt"] = datetime.now().isoformat()
                marked = True
                break
            else:
                raise TaskError(f"Task {task_id} already has status {status.value}.")
    if marked:
        save_tasks(data)
        return f"Task with id {task_id} marked as {status.value}."
    else:
        raise TaskError(f"Task with id {task_id} not found.")

def mark_in_progress(task_id: int) -> str:
    return set_status(task_id, Status.IN_PROGRESS)

def mark_done(task_id: int) -> str:
    return set_status(task_id, Status.DONE)

def mark_todo(task_id: int) -> str:
    return set_status(task_id, Status.TODO)