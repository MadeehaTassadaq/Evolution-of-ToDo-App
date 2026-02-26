from datetime import datetime, timedelta
import pytest
from src.models.task import Task
from src.models.task_list import TaskList
from src.models.recurrence_rule import RecurrenceRule
from src.services.task_service import TaskService
from src.services.search_service import SearchService
from src.services.recurrence_service import RecurrenceService
from src.lib.validators import ValidationError
from src.lib.utils import generate_task_id


@pytest.fixture
def task_list_service():
    task_list = TaskList()
    recurrence_service = RecurrenceService()
    service = TaskService(task_list, recurrence_service)
    return service


@pytest.fixture
def search_service():
    return SearchService()


@pytest.fixture
def populate_tasks(task_list_service):
    task1 = task_list_service.create_task("Task Alpha", priority="high", tags=["work"])
    task2 = task_list_service.create_task("Task Beta", priority="medium", due_date=(datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d %H:%M"))
    task3 = task_list_service.create_task("Task Gamma", priority="low", tags=["home"])
    task4 = task_list_service.create_task("Task Delta", description="report task", tags=["work"], due_date=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"))
    return task1, task2, task3, task4


# Test TaskService
def test_task_service_create_task(task_list_service):
    task = task_list_service.create_task("New Task", description="Some desc", priority="low")
    assert task.title == "New Task"
    assert task.description == "Some desc"
    assert task.priority == "low"
    assert task_list_service.get_task(task.id) == task


def test_task_service_create_task_invalid_title(task_list_service):
    with pytest.raises(ValidationError, match="Title cannot be empty"):
        task_list_service.create_task("")


def test_task_service_get_task(task_list_service, populate_tasks):
    task1, _, _, _ = populate_tasks
    retrieved_task = task_list_service.get_task(task1.id)
    assert retrieved_task == task1


def test_task_service_get_all_tasks(task_list_service, populate_tasks):
    tasks = task_list_service.get_all_tasks()
    assert len(tasks) == 4


def test_task_service_update_task(task_list_service, populate_tasks):
    task1, _, _, _ = populate_tasks
    updated_task = task_list_service.update_task(task1.id, title="Updated Title", priority="medium")
    assert updated_task.title == "Updated Title"
    assert updated_task.priority == "medium"
    assert task_list_service.get_task(task1.id).title == "Updated Title"


def test_task_service_update_task_invalid_priority(task_list_service, populate_tasks):
    task1, _, _, _ = populate_tasks
    with pytest.raises(ValidationError, match="Priority must be 'high', 'medium', or 'low'"):
        task_list_service.update_task(task1.id, priority="invalid")


def test_task_service_delete_task(task_list_service, populate_tasks):
    task1, _, _, _ = populate_tasks
    task_list_service.delete_task(task1.id)
    assert task_list_service.get_task(task1.id) is None
    assert len(task_list_service.get_all_tasks()) == 3


def test_task_service_toggle_complete(task_list_service, populate_tasks):
    task1, _, _, _ = populate_tasks
    assert not task1.completed
    completed_task = task_list_service.toggle_complete(task1.id)
    assert completed_task.completed
    incomplete_task = task_list_service.toggle_complete(task1.id)
    assert not incomplete_task.completed


def test_task_service_add_tag(task_list_service, populate_tasks):
    task1, _, _, _ = populate_tasks
    task_list_service.add_tag(task1.id, "urgent")
    assert "urgent" in task_list_service.get_task(task1.id).tags


def test_task_service_remove_tag(task_list_service, populate_tasks):
    task1, _, _, _ = populate_tasks
    task_list_service.remove_tag(task1.id, "work")
    assert "work" not in task_list_service.get_task(task1.id).tags


def test_task_service_is_overdue(task_list_service, populate_tasks):
    _, _, _, overdue_task = populate_tasks
    assert task_list_service.is_overdue(overdue_task.id)


# Test SearchService
def test_search_service_search_tasks(task_list_service, search_service, populate_tasks):
    tasks = task_list_service.get_all_tasks()
    results = search_service.search_tasks(tasks, "task")
    assert len(results) == 4
    results = search_service.search_tasks(tasks, "alpha")
    assert len(results) == 1
    assert results[0].title == "Task Alpha"
    results = search_service.search_tasks(tasks, "work")
    assert len(results) == 2


def test_search_service_filter_by_status(task_list_service, search_service, populate_tasks):
    task1, _, _, _ = populate_tasks
    task_list_service.toggle_complete(task1.id)
    tasks = task_list_service.get_all_tasks()
    completed_tasks = search_service.filter_by_status(tasks, True)
    assert len(completed_tasks) == 1
    assert completed_tasks[0].id == task1.id


def test_search_service_filter_by_priority(task_list_service, search_service, populate_tasks):
    tasks = task_list_service.get_all_tasks()
    high_priority_tasks = search_service.filter_by_priority(tasks, "high")
    assert len(high_priority_tasks) == 1
    assert high_priority_tasks[0].title == "Task Alpha"


def test_search_service_filter_by_tag(task_list_service, search_service, populate_tasks):
    tasks = task_list_service.get_all_tasks()
    work_tags = search_service.filter_by_tag(tasks, "work")
    assert len(work_tags) == 2


def test_search_service_sort_by_due_date(task_list_service, search_service, populate_tasks):
    tasks = task_list_service.get_all_tasks()
    sorted_tasks = search_service.sort_by_due_date(tasks)
    # The overdue task should come first
    assert sorted_tasks[0].description == "report task"
    # Task with a future due date
    assert sorted_tasks[1].title == "Task Beta"


def test_search_service_sort_by_priority(task_list_service, search_service, populate_tasks):
    tasks = task_list_service.get_all_tasks()
    sorted_tasks = search_service.sort_by_priority(tasks)
    assert sorted_tasks[0].priority == "high"
    assert sorted_tasks[1].priority == "medium"
    assert sorted_tasks[2].priority == "low"


def test_search_service_sort_by_title(task_list_service, search_service, populate_tasks):
    tasks = task_list_service.get_all_tasks()
    sorted_tasks = search_service.sort_by_title(tasks)
    assert sorted_tasks[0].title == "Task Alpha"
    assert sorted_tasks[1].title == "Task Beta"
    assert sorted_tasks[2].title == "Task Delta"
    assert sorted_tasks[3].title == "Task Gamma"


def test_search_service_filter_by_due_date_range(task_list_service, search_service):
    # Setup tasks with specific due dates
    now = datetime.now()
    t1 = task_list_service.create_task("Today Task", due_date=now.strftime("%Y-%m-%d %H:%M"))
    t2 = task_list_service.create_task("Tomorrow Task", due_date=(now + timedelta(days=1)).strftime("%Y-%m-%d %H:%M"))
    t3 = task_list_service.create_task("Next Week Task", due_date=(now + timedelta(weeks=1)).strftime("%Y-%m-%d %H:%M"))

    tasks = task_list_service.get_all_tasks()

    # Filter for today and tomorrow
    start_date = now - timedelta(hours=1)
    end_date = now + timedelta(days=1, hours=1)
    results = search_service.filter_by_due_date_range(tasks, start_date, end_date)
    assert len(results) == 2
    assert t1 in results
    assert t2 in results
    assert t3 not in results


def test_search_service_get_overdue_tasks(task_list_service, search_service):
    # Setup tasks
    task_list_service.create_task("Overdue 1", due_date=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"))
    task_list_service.create_task("Not Overdue", due_date=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M"))
    tasks = task_list_service.get_all_tasks()
    overdue_tasks = search_service.get_overdue_tasks(tasks)
    assert len(overdue_tasks) == 1
    assert "Overdue 1" in [t.title for t in overdue_tasks]


def test_search_service_get_upcoming_tasks(task_list_service, search_service):
    # Setup tasks
    task_list_service.create_task("Upcoming 1", due_date=(datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"))
    task_list_service.create_task("Upcoming 2", due_date=(datetime.now() + timedelta(hours=23)).strftime("%Y-%m-%d %H:%M"))
    task_list_service.create_task("Too Far", due_date=(datetime.now() + timedelta(hours=25)).strftime("%Y-%m-%d %H:%M"))
    tasks = task_list_service.get_all_tasks()
    upcoming_tasks = search_service.get_upcoming_tasks(tasks, 24)
    assert len(upcoming_tasks) == 2
    assert "Upcoming 1" in [t.title for t in upcoming_tasks]
    assert "Upcoming 2" in [t.title for t in upcoming_tasks]


# Test RecurrenceService
@pytest.fixture
def recurrence_service_fixture():
    return RecurrenceService()


def test_recurrence_service_calculate_next_due_date_daily(recurrence_service_fixture):
    current_due = datetime(2026, 1, 1, 10, 0)
    rule = RecurrenceRule(interval_type="daily", interval_count=1)
    next_due = recurrence_service_fixture.calculate_next_due_date(current_due, rule)
    assert next_due == datetime(2026, 1, 2, 10, 0)


def test_recurrence_service_calculate_next_due_date_weekly(recurrence_service_fixture):
    current_due = datetime(2026, 1, 1, 10, 0)
    rule = RecurrenceRule(interval_type="weekly", interval_count=2)
    next_due = recurrence_service_fixture.calculate_next_due_date(current_due, rule)
    assert next_due == datetime(2026, 1, 15, 10, 0)


def test_recurrence_service_generate_next_occurrence(task_list_service, recurrence_service_fixture):
    rule = RecurrenceRule(interval_type="daily", interval_count=1)
    initial_task = task_list_service.create_task(
        "Daily Meeting",
        due_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
        recurrence=rule
    )
    
    # Manually assign recurrence rule to the task for the generate_next_occurrence method to work
    initial_task.recurrence = rule
    
    next_occurrence = recurrence_service_fixture.generate_next_occurrence(initial_task, task_list_service)
    assert next_occurrence.title == "Daily Meeting"
    assert next_occurrence.completed is False
    assert next_occurrence.due_date > initial_task.due_date
    assert task_list_service.get_task(next_occurrence.id) is not None
