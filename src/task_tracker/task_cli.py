import argparse
import json
import sys
from .task_functions import Status, add, update, delete, list_tasks, mark_done, mark_in_progress, mark_todo, TaskError

def cli():
    global_parser = argparse.ArgumentParser()
    subparsers = global_parser.add_subparsers(
        title="subcommands", help="task management commands", dest="command"
    )

    add_parser = subparsers.add_parser("add", help="Add new task to a JSON file")
    add_parser.add_argument("description", type=str, help="The task description")
    add_parser.add_argument("status", type=Status.from_string, nargs="?", default="todo", help="The initial status")
    add_parser.set_defaults(func=add)

    update_parser = subparsers.add_parser("update", help="Update an existing task.")
    update_parser.add_argument("task_id", metavar="id", type=int, help="Id of the task.")
    update_parser.add_argument("description", type=str, help="New task description.")
    update_parser.set_defaults(func=update)

    delete_parser = subparsers.add_parser("delete", help="Delete a task.")
    delete_parser.add_argument("task_id", metavar="id", type=int, help="Id of the task.")
    delete_parser.set_defaults(func=delete)

    list_parser = subparsers.add_parser("list", help="List all JSON tasks.")
    list_parser.add_argument("status", type=Status.from_string, nargs='?', metavar="STATUS", help="List tasks with given status.")
    list_parser.set_defaults(func=list_tasks)

    mark_in_progress_parser = subparsers.add_parser("mark-in-progress", help="Mark task as in progress.")
    mark_in_progress_parser.add_argument("task_id", metavar="id", type=int, help="Id of the task.")
    mark_in_progress_parser.set_defaults(func=mark_in_progress)

    mark_done_parser = subparsers.add_parser("mark-done", help="Mark task as done.")
    mark_done_parser.add_argument("task_id", metavar="id", type=int, help="Id of the task.")
    mark_done_parser.set_defaults(func=mark_done)

    mark_todo_parser = subparsers.add_parser("mark-todo", help="Mark task as todo.")
    mark_todo_parser.add_argument("task_id", metavar="id", type=int, help="Id of the task.")
    mark_todo_parser.set_defaults(func=mark_todo)

    args = global_parser.parse_args()

    if not hasattr(args, "func"):
        global_parser.print_help()
        sys.exit(1)

    kwargs = vars(args)
    func = kwargs.pop("func")
    kwargs.pop("command")

    try:
        result = func(**kwargs)
        if isinstance(result, list):
            print("\n".join(result))
        else:
            print(result)
    except TaskError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: task file is corrupted.", file=sys.stderr)
        sys.exit(1)
    