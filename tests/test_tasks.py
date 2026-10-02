import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from task_tracker import task_functions
from task_tracker.task_cli import cli
from task_tracker.task_functions import (
    Status,
    TaskError,
    add,
    delete,
    list_tasks,
    mark_done,
    mark_in_progress,
    mark_todo,
    update,
)


class TaskTestCase(unittest.TestCase):
    """Base class: every test gets its own empty temp directory for the JSON file."""
    def setUp(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        self.file_path = Path(tmp_dir.name) / "tasks.json"

        # Point to the temporary directory instead of real file:
        patcher = patch.object(task_functions, "FILE_PATH", self.file_path)
        patcher.start()
        self.addCleanup(patcher.stop)

    def read_tasks(self) -> list[dict]:
        """Read the JSON file directly"""
        with open(self.file_path, 'r', encoding='UTF-8') as f:
            return json.load(f)["tasks"]

class TestAdd(TaskTestCase):

    def test_creates_file_when_missing(self):
        self.assertFalse(self.file_path.exists())
        add("Buy groceries", Status.TODO)
        self.assertTrue(self.file_path.exists())

    def test_first_task_gets_id_1(self):
        add("Buy groceries", Status.TODO)
        self.assertEqual(self.read_tasks()[0]["id"], 1)

    def test_saves_all_required_field(self):
        add("Buy groceries.", Status.TODO)
        task = self.read_tasks()[0]
        self.assertEqual(
            set(task.keys()),
            {"id", "description", "status", "createdAt", "updatedAt"},
        )
        self.assertEqual(task["description"], "Buy groceries.")
        self.assertEqual(task["status"], "todo")

    def test_ids_increase(self):
        add("First", Status.TODO)
        add("Second", Status.TODO)
        self.assertEqual([task["id"] for task in self.read_tasks()], [1, 2])

    def test_empty_description_raises(self):
        with self.assertRaises(TaskError):
            add("   ", Status.TODO)

class TestDelete(TaskTestCase):

    def test_other_ids_do_not_change(self):
        add("A", Status.TODO)
        add("B", Status.TODO)
        add("C", Status.TODO)
        delete(2)
        self.assertEqual([task["id"] for task in self.read_tasks()], [1,3])

    def test_new_id_after_delete_is_not_reused(self):
        add("A", Status.TODO)
        add("B", Status.TODO)
        add("C", Status.TODO)
        delete(2)
        add("D", Status.TODO)
        self.assertEqual(self.read_tasks()[-1]["id"], 4)

    def test_missing_id_raises(self):
        add("A", Status.TODO)
        with self.assertRaises(TaskError):
            delete(2)

class TestUpdate(TaskTestCase):

    def test_changes_description_and_updated_at(self):
        created = datetime(2026, 1, 1, 12, 0, 0)
        updated = datetime(2026, 1, 1, 12, 5, 0)        
        with patch.object(task_functions, "datetime") as fake_datetime:
            fake_datetime.now.side_effect= [created, updated]
            add("Old", Status.TODO)
            update(1, "New")

        after = self.read_tasks()[0]
        self.assertEqual(after["description"], "New")
        self.assertEqual(after["createdAt"], created.isoformat())
        self.assertEqual(after["updatedAt"], updated.isoformat())

    def test_empty_description_raises(self):
        add("A", Status.TODO)
        with self.assertRaises(TaskError):
            update(1, " ")

    def test_missing_id_raises(self):
        add("A", Status.TODO)
        with self.assertRaises(TaskError):
            update(99, "B")

class TestSetStatus(TaskTestCase):

    def test_mark_done(self):
        add("A", Status.TODO)
        mark_done(1)
        self.assertEqual(self.read_tasks()[0]["status"], "done")

    def test_mark_in_progress(self):
        add("A", Status.TODO)
        mark_in_progress(1)
        self.assertEqual(self.read_tasks()[0]["status"], "in-progress")

    def test_mark_todo(self):
        add("A", Status.DONE)
        mark_todo(1)
        self.assertEqual(self.read_tasks()[0]["status"], "todo")

    def test_missing_id_raises(self):
        add("A", Status.TODO)
        with self.assertRaises(TaskError):
            mark_done(99)

    def test_same_status_raises(self):
        add("A", Status.TODO)
        with self.assertRaises(TaskError):
            mark_todo(1) 

class TestListTask(TaskTestCase):

    def test_lists_all(self):
        add("A", Status.TODO)
        add("B", Status.DONE)
        self.assertEqual(list_tasks(None), ["[1] todo: A", "[2] done: B"])

    def test_filters_by_status(self):
        add("A", Status.TODO)
        add("B", Status.DONE)
        self.assertEqual(list_tasks(Status.DONE), ["[2] done: B"])

    def test_empty_list_raises(self):
        with self.assertRaises(TaskError):
            list_tasks(None)

    def test_no_tasks_with_status_raises(self):
        add("A", Status.TODO)
        with self.assertRaises(TaskError):
            list_tasks(Status.DONE)

class TestStatusFromString(unittest.TestCase):

    def test_normalizes_input(self):
        self.assertEqual(Status.from_string("   IN-PROGRESS  "), Status.IN_PROGRESS)

    def test_invalid_value_raises(self):
        with self.assertRaises(ValueError):
            Status.from_string("finished")

class TestCli(TaskTestCase):

    def run_cli(self, *args):
        """Run the CLI as if the user typed in command."""
        buffer = io.StringIO()
        with patch.object(sys, "argv", ["tasks", *args]), redirect_stdout(buffer):
            cli()
        return buffer.getvalue()

    def test_update_via_cli(self):
        self.run_cli("add", "Old")
        self.run_cli("update", "1", "New")
        self.assertEqual(self.read_tasks()[0]["description"], "New")

    def test_delete_via_cli(self):
        self.run_cli("add", "A")
        self.run_cli("delete", "1")
        self.assertEqual(self.read_tasks(), [])

    def test_mark_commands_via_cli(self):
        self.run_cli("add", "A")
        self.run_cli("mark-in-progress", "1")
        self.assertEqual(self.read_tasks()[0]["status"], "in-progress")
        self.run_cli("mark-done", "1")
        self.assertEqual(self.read_tasks()[0]["status"], "done")
        self.run_cli("mark-todo", "1")
        self.assertEqual(self.read_tasks()[0]["status"], "todo")

    def test_list_via_cli(self):
        self.run_cli("add", "A")
        self.run_cli("add", "B", "done")
        self.assertEqual(self.run_cli("list"), "[1] todo: A\n[2] done: B\n")
        self.assertEqual(self.run_cli("list", "done"), "[2] done: B\n")


if __name__ == "__main__":
    unittest.main()