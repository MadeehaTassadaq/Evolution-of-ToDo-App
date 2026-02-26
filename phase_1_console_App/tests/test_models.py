from datetime import datetime, timedelta
import pytest
from src.models.task import Task
from src.models.recurrence_rule import RecurrenceRule
from src.models.task_list import TaskList
from src.lib.utils import generate_task_id


# Test Task Model
def test_task_creation():
    task = Task(id=generate_task_id(), title="Test Task")
    assert task.title == "Test Task"
    assert not task.completed
    assert task.priority is None
    assert task.tags == []


def test_task_toggle_complete():
    task = Task(id=generate_task_id(), title="Test Task")
    task.toggle_complete()
    assert task.completed
    task.toggle_complete()
    assert not task.completed


def test_task_is_overdue_false():
    future_date = datetime.now() + timedelta(days=1)
    task = Task(id=generate_task_id(), title="Future Task", due_date=future_date)
    assert not task.is_overdue()


def test_task_is_overdue_true():
    past_date = datetime.now() - timedelta(days=1)
    task = Task(id=generate_task_id(), title="Past Task", due_date=past_date)
    assert task.is_overdue()


def test_task_add_tag():
    task = Task(id=generate_task_id(), title="Test Task")
    task.add_tag("work")
    assert "work" in task.tags
    task.add_tag("urgent")
    assert "urgent" in task.tags
    assert len(task.tags) == 2


def test_task_remove_tag():
    task = Task(id=generate_task_id(), title="Test Task", tags=["work", "urgent"])
    task.remove_tag("work")
    assert "work" not in task.tags
    assert "urgent" in task.tags
    assert len(task.tags) == 1


# Test RecurrenceRule Model
def test_recurrence_rule_creation():
    rule = RecurrenceRule(interval_type="daily", interval_count=1)
    assert rule.interval_type == "daily"
    assert rule.interval_count == 1


def test_recurrence_rule_invalid_interval_count():
    with pytest.raises(ValueError, match="interval_count must be at least 1"):
        RecurrenceRule(interval_type="daily", interval_count=0)


def test_recurrence_rule_invalid_interval_type():
    with pytest.raises(ValueError, match="interval_type must be one of"):
        RecurrenceRule(interval_type="invalid", interval_count=1)


# Test TaskList Model
@pytest.fixture
def empty_task_list():
    return TaskList()


@pytest.fixture
def populated_task_list():
    task_list = TaskList()
    task1 = Task(id="1", title="Task 1")
    task2 = Task(id="2", title="Task 2")
    task_list.add(task1)
    task_list.add(task2)
    return task_list


def test_task_list_add(empty_task_list):
    task = Task(id="1", title="New Task")
    empty_task_list.add(task)
    assert empty_task_list.get("1") == task
    assert empty_task_list.count() == 1


def test_task_list_add_duplicate(populated_task_list):
    task = Task(id="1", title="Duplicate Task")
    with pytest.raises(ValueError, match="already exists"):
        populated_task_list.add(task)


def test_task_list_get(populated_task_list):
    task = populated_task_list.get("1")
    assert task.title == "Task 1"
    assert populated_task_list.get("nonexistent") is None


def test_task_list_all(populated_task_list):
    tasks = populated_task_list.all()
    assert len(tasks) == 2
    assert tasks[0].title == "Task 1"
    assert tasks[1].title == "Task 2"


def test_task_list_update(populated_task_list):
    task = populated_task_list.get("1")
    task.title = "Updated Task 1"
    populated_task_list.update(task)
    assert populated_task_list.get("1").title == "Updated Task 1"


def test_task_list_update_nonexistent(empty_task_list):
    task = Task(id="1", title="Nonexistent")
    with pytest.raises(KeyError, match="not found"):
        empty_task_list.update(task)


def test_task_list_delete(populated_task_list):
    populated_task_list.delete("1")
    assert populated_task_list.get("1") is None
    assert populated_task_list.count() == 1


def test_task_list_delete_nonexistent(empty_task_list):
    with pytest.raises(KeyError, match="not found"):
        empty_task_list.delete("nonexistent")


def test_task_list_exists(populated_task_list):
    assert populated_task_list.exists("1")
    assert not populated_task_list.exists("nonexistent")


def test_task_list_count(populated_task_list):
    assert populated_task_list.count() == 2


def test_task_list_clear(populated_task_list):
    populated_task_list.clear()
    assert populated_task_list.count() == 0
