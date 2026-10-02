# Task Tracker CLI

A simple command-line tool to track and manage your tasks — what you need to do, what you're working on, and what you've already done.

Built in pure Python with no external dependencies, as a solution to the [Task Tracker](https://roadmap.sh/projects/task-tracker) project from roadmap.sh.

## Features

- Add, update and delete tasks
- Mark tasks as `todo`, `in-progress` or `done`
- List all tasks, or filter them by status
- Tasks are stored in a JSON file in the current directory (created automatically on first use)
- Clear error messages and non-zero exit codes when something goes wrong

## Requirements

- Python 3.12 or newer
- No third-party packages — only the Python standard library

## Installation

```bash
git clone https://github.com/xliquidskyx/task_tracker_cli.git
cd task_tracker_cli

python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

pip install -e .
```

This installs the `tasks` command into your virtual environment. Thanks to `-e` (editable mode), any change you make to the source code is picked up immediately.

## Usage

```bash
# Add a new task (status defaults to "todo")
tasks add "Buy groceries"
# You have added a new task with id 1.

# Add a task with an initial status
tasks add "Write README" in-progress

# Update a task's description
tasks update 1 "Buy groceries and cook dinner"

# Delete a task
tasks delete 1

# Change a task's status
tasks mark-in-progress 1
tasks mark-done 1
tasks mark-todo 1

# List all tasks
tasks list

# List tasks by status
tasks list todo
tasks list in-progress
tasks list done
```

Status values are case-insensitive and accept underscores, so `IN_PROGRESS`, `in_progress` and `in-progress` all work.

Run `tasks --help` or `tasks <command> --help` to see all options.

### Example session

```text
$ tasks add "Buy groceries" done
You have added a new task with id 1.
$ tasks add "Cook dinner"
You have added a new task with id 2.
$ tasks list
[1] done: Buy groceries
[2] todo: Cook dinner
All the tasks have been listed.
```

## Data storage

Tasks are saved to `task_cli.json` in the directory you run the command from. Each directory therefore has its own task list. The file is created automatically when you add your first task.

Each task has the following properties:

| Field         | Description                                    |
|---------------|------------------------------------------------|
| `id`          | Unique identifier — never reused or renumbered |
| `description` | Short description of the task                  |
| `status`      | `todo`, `in-progress` or `done`                |
| `createdAt`   | Date and time the task was created (ISO 8601)  |
| `updatedAt`   | Date and time the task was last updated        |

Example file:

```json
{
    "tasks": [
        {
            "id": 1,
            "description": "Buy groceries",
            "status": "done",
            "createdAt": "2026-09-30T10:15:42.120391",
            "updatedAt": "2026-09-30T10:20:03.551204"
        }
    ]
}
```

## Error handling

Errors are printed to `stderr` and the program exits with code `1`, so the tool behaves correctly in scripts:

```text
$ tasks delete 99
Error: Task with id 99 not found.
$ echo $?
1
```

Handled cases include: unknown task id, empty description, setting a status the task already has, an empty task list, and a corrupted JSON file. Invalid arguments (e.g. an unknown status) are reported by `argparse` with exit code `2`.

## Running tests

Tests use the built-in `unittest` module. Each test runs against its own temporary file, so your real tasks are never touched.

```bash
python -m unittest discover -s tests -v
```

## Project structure

```text
task_tracker_cli/
├── pyproject.toml              # package metadata and the `tasks` entry point
├── src/
│   └── task_tracker/
│       ├── main.py             # entry point
│       ├── task_cli.py         # argument parsing and error reporting
│       └── task_functions.py   # task logic and JSON storage
└── tests/
    └── test_tasks.py           # unit tests
```
