import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from task_tracker import task_functions
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

    def test_new_id_after_delete_is_not_resued(self):
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

class TaskUpdate(TaskTestCase):

    def test_changes_description_and_updated_at(self):
        add("Old", Status.TODO)
        before = self.read_tasks()[0]
        update(1, "New")
        after = self.read_tasks()[0]
        self.assertEqual(after["description"], "New")
        self.assertEqual(after["createdAt"], before["createdAt"])
        self.assertNotEqual(before["updatedAt"], after["updatedAt"])

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

class TestListTask(TaskTestCase):

    def run_list(self, status):
        """Capture what list_tasks prints to the terminal"""
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            list_tasks(status)
        return buffer.getvalue()

    def test_lists_all(self):
        add("A", Status.TODO)
        add("B", Status.DONE)
        output = self.run_list(None)
        self.assertIn("A", output)
        self.assertIn("B", output)

    def test_filters_by_status(self):
        add("A", Status.TODO)
        add("B", Status.DONE)
        output = self.run_list(Status.DONE)
        self.assertIn("B", output)
        self.assertNotIn("A", output)

    def test_empy_list_raises(self):
        with self.assertRaises(TaskError):
            list_tasks(None)

class TestStatusFromString(unittest.TestCase):

    def test_normalizes_input(self):
        self.assertEqual(Status.from_string("   IN-PROGRESS  "), Status.IN_PROGRESS)

    def test_invalid_value_raises(self):
        with self.assertRaises(Exception):
            Status.from_string("finished")

if __name__ == "__main__":
    unittest.main()