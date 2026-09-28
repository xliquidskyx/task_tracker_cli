import argparse
from task_functions import Status, add, update, delete, list_tasks, mark_done, mark_in_progress

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

mark_in_progress_parser = subparsers.add_parser("mark-in-progress", help="Mark task as in progress.")
mark_in_progress_parser.add_argument("id", type=int, help="Id of the task.")
mark_in_progress_parser.set_defaults(func=mark_in_progress)

mark_done_parser = subparsers.add_parser("mark-done", help="Mark task as done.")
mark_done_parser.add_argument("id", type=int, help="Id of the task.")
mark_done_parser.set_defaults(func=mark_done)

args = global_parser.parse_args()

if args.command == "add":
    print(args.func(args.description, args.status))
elif args.command == "update":
    print(args.func(args.id, args.description, args.status))
elif args.command == "delete" or args.command == "mark-in-progress" or args.command == "mark-done":
    print(args.func(args.id))
elif args.command == "list":
    print(args.func(args.status))
else:
    global_parser.print_help()