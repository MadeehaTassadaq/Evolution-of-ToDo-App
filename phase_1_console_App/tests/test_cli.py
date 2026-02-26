import pytest
from unittest.mock import MagicMock
from src.cli.parser import CommandParser
from src.cli.renderer import Renderer
from src.cli.commands import CommandHandler
from src.services.task_service import TaskService
from src.services.search_service import SearchService
from src.lib.validators import ValidationError
from src.models.task import Task
from src.models.task_list import TaskList
from src.models.recurrence_rule import RecurrenceRule


@pytest.fixture
def parser():
    return CommandParser()


@pytest.fixture
def mock_task_service():
    service = MagicMock(spec=TaskService)
    service.create_task.return_value = Task(id="mock-id", title="Mock Task")
    service.get_task.return_value = Task(id="mock-id", title="Mock Task", completed=False)
    service.get_all_tasks.return_value = [
        Task(id="id1", title="Task 1"),
        Task(id="id2", title="Task 2", completed=True)
    ]
    service.update_task.return_value = Task(id="mock-id", title="Updated Task")
    service.delete_task.return_value = None
    service.toggle_complete.return_value = Task(id="mock-id", title="Mock Task", completed=True)
    service.add_tag.return_value = None
    service.remove_tag.return_value = None
    service.is_overdue.return_value = False
    return service


@pytest.fixture
def mock_search_service():
    service = MagicMock(spec=SearchService)
    service.search_tasks.return_value = []
    service.filter_by_status.return_value = []
    service.filter_by_priority.return_value = []
    service.filter_by_tag.return_value = []
    service.sort_by_due_date.return_value = []
    service.sort_by_priority.return_value = []
    service.sort_by_title.return_value = []
    service.filter_by_due_date_range.return_value = []
    service.get_overdue_tasks.return_value = []
    service.get_upcoming_tasks.return_value = []
    return service


@pytest.fixture
def renderer():
    return Renderer()


@pytest.fixture
def command_handler(mock_task_service, mock_search_service, renderer):
    return CommandHandler(mock_task_service, mock_search_service, renderer)


# Test CommandParser
def test_parse_add_command(parser):
    cmd = parser.parse("add 'Buy groceries' -d 'Milk and eggs' -p high -t home urgent --due-date '2026-01-15 09:00'")
    assert cmd['command'] == 'add'
    assert cmd['title'] == 'Buy groceries'
    assert cmd['description'] == 'Milk and eggs'
    assert cmd['priority'] == 'high'
    assert cmd['tags'] == ['home', 'urgent']
    assert cmd['due_date'] == '2026-01-15 09:00'


def test_parse_list_command(parser):
    cmd = parser.parse("list")
    assert cmd['command'] == 'list'


def test_parse_update_command(parser):
    cmd = parser.parse("update task-123 --title 'New Title' -p medium")
    assert cmd['command'] == 'update'
    assert cmd['task_id'] == 'task-123'
    assert cmd['title'] == 'New Title'
    assert cmd['priority'] == 'medium'


def test_parse_delete_command(parser):
    cmd = parser.parse("delete task-123")
    assert cmd['command'] == 'delete'
    assert cmd['task_id'] == 'task-123'


def test_parse_complete_command(parser):
    cmd = parser.parse("complete task-123")
    assert cmd['command'] == 'complete'
    assert cmd['task_id'] == 'task-123'


def test_parse_search_command(parser):
    cmd = parser.parse("search keyword")
    assert cmd['command'] == 'search'
    assert cmd['keyword'] == 'keyword'


def test_parse_filter_command(parser):
    cmd = parser.parse("filter status completed")
    assert cmd['command'] == 'filter'
    assert cmd['filter_by'] == 'status'
    assert cmd['value'] == 'completed'


def test_parse_sort_command(parser):
    cmd = parser.parse("sort priority")
    assert cmd['command'] == 'sort'
    assert cmd['sort_by'] == 'priority'


def test_parse_tag_command(parser):
    cmd = parser.parse("tag task-123 add work")
    assert cmd['command'] == 'tag'
    assert cmd['task_id'] == 'task-123'
    assert cmd['action'] == 'add'
    assert cmd['tags'] == ['work']


def test_parse_overdue_command(parser):
    cmd = parser.parse("overdue")
    assert cmd['command'] == 'overdue'


def test_parse_upcoming_command(parser):
    cmd = parser.parse("upcoming 48")
    assert cmd['command'] == 'upcoming'
    assert cmd['hours'] == 48


def test_parse_invalid_command(parser):
    cmd = parser.parse("nonexistent command")
    assert cmd is None


# Test CommandHandler
def test_handle_add(command_handler, mock_task_service):
    cmd = {'command': 'add', 'title': 'Test Add'}
    result = command_handler.handle_add(cmd)
    mock_task_service.create_task.assert_called_with(title='Test Add', description=None, priority=None, tags=None, due_date=None)
    assert "Task created successfully" in result


def test_handle_list(command_handler, mock_task_service):
    cmd = {'command': 'list'}
    result = command_handler.handle_list(cmd)
    mock_task_service.get_all_tasks.assert_called_once()
    assert "Task 1" in result


def test_handle_update(command_handler, mock_task_service):
    task = Task(id="id1", title="Original Title")
    mock_task_service.get_task.return_value = task
    cmd = {'command': 'update', 'task_id': 'id1', 'title': 'Updated Title'}
    result = command_handler.handle_update(cmd)
    mock_task_service.update_task.assert_called_with(task.id, title='Updated Title')
    assert "Task updated successfully" in result


def test_handle_delete(command_handler, mock_task_service):
    task = Task(id="id1", title="To Delete")
    mock_task_service.get_task.return_value = task
    cmd = {'command': 'delete', 'task_id': 'id1'}
    result = command_handler.handle_delete(cmd)
    mock_task_service.delete_task.assert_called_with(task.id)
    assert "Task deleted successfully" in result


def test_handle_complete(command_handler, mock_task_service):
    task = Task(id="id1", title="To Complete", completed=False)
    mock_task_service.get_task.return_value = task
    mock_task_service.toggle_complete.return_value = Task(id="id1", title="To Complete", completed=True)
    cmd = {'command': 'complete', 'task_id': 'id1'}
    result = command_handler.handle_complete(cmd)
    mock_task_service.toggle_complete.assert_called_with(task.id)
    assert "marked as completed" in result


def test_handle_search(command_handler, mock_task_service, mock_search_service):
    mock_task_service.get_all_tasks.return_value = [Task(id="id1", title="Found Task")]
    mock_search_service.search_tasks.return_value = [Task(id="id1", title="Found Task")]
    cmd = {'command': 'search', 'keyword': ['Found']}
    result = command_handler.handle_search(cmd)
    mock_search_service.search_tasks.assert_called_once_with([Task(id="id1", title="Found Task")], 'Found')
    assert "Found Task" in result


def test_handle_filter_status(command_handler, mock_task_service, mock_search_service):
    mock_task_service.get_all_tasks.return_value = [Task(id="id1", title="Completed Task", completed=True)]
    mock_search_service.filter_by_status.return_value = [Task(id="id1", title="Completed Task", completed=True)]
    cmd = {'command': 'filter', 'filter_by': 'status', 'value': 'completed'}
    result = command_handler.handle_filter(cmd)
    mock_search_service.filter_by_status.assert_called_once_with([Task(id="id1", title="Completed Task", completed=True)], True)
    assert "Completed Task" in result


def test_handle_sort_priority(command_handler, mock_task_service, mock_search_service):
    mock_task_service.get_all_tasks.return_value = [Task(id="id1", title="High Priority", priority="high")]
    mock_search_service.sort_by_priority.return_value = [Task(id="id1", title="High Priority", priority="high")]
    cmd = {'command': 'sort', 'sort_by': 'priority'}
    result = command_handler.handle_sort(cmd)
    mock_search_service.sort_by_priority.assert_called_once_with([Task(id="id1", title="High Priority", priority="high")])
    assert "High Priority" in result


def test_handle_tag_add(command_handler, mock_task_service):
    task = Task(id="id1", title="Tag Task")
    mock_task_service.get_task.return_value = task
    mock_task_service.get_all_tasks.return_value = [task] # Ensure _find_task_by_short_id can find it
    cmd = {'command': 'tag', 'task_id': 'id1', 'action': 'add', 'tags': ['newtag']}
    result = command_handler.handle_tag(cmd)
    mock_task_service.add_tag.assert_called_with(task.id, 'newtag')
    assert f"Tags added to task '{task.title}'" in result


def test_handle_overdue(command_handler, mock_task_service, mock_search_service):
    mock_task_service.get_all_tasks.return_value = [Task(id="id1", title="Overdue Task")]
    mock_search_service.get_overdue_tasks.return_value = [Task(id="id1", title="Overdue Task")]
    cmd = {'command': 'overdue'}
    result = command_handler.handle_overdue(cmd)
    mock_search_service.get_overdue_tasks.assert_called_once_with([Task(id="id1", title="Overdue Task")])
    assert "Overdue Task" in result


def test_handle_upcoming(command_handler, mock_task_service, mock_search_service):
    mock_task_service.get_all_tasks.return_value = [Task(id="id1", title="Upcoming Task")]
    mock_search_service.get_upcoming_tasks.return_value = [Task(id="id1", title="Upcoming Task")]
    cmd = {'command': 'upcoming', 'hours': 48}
    result = command_handler.handle_upcoming(cmd)
    mock_search_service.get_upcoming_tasks.assert_called_once_with([Task(id="id1", title="Upcoming Task")], 48)
    assert "Upcoming Task" in result
