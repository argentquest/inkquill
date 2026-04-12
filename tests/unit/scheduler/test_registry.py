"""Unit tests for the scheduler task registry."""

import pytest
from app.scheduler.registry import register_task, get_task, list_tasks, _TASKS

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def clear_registry():
    """Clear the task registry before each test."""
    _TASKS.clear()
    yield
    _TASKS.clear()


def test_register_task_adds_to_registry():
    """@register_task adds a task definition to the global registry."""

    @register_task(key="test.task", name="Test Task", default_cron="0 * * * *")
    async def my_task():
        pass

    task = get_task("test.task")
    assert task is not None
    assert task.name == "Test Task"
    assert task.default_cron == "0 * * * *"
    assert task.enabled_by_default is True


def test_register_task_with_custom_options():
    """@register_task accepts custom options."""

    @register_task(
        key="test.custom",
        name="Custom Task",
        default_cron="0 8 * * *",
        description="A custom task",
        enabled_by_default=False,
        max_instances=3,
        misfire_grace_time=600,
    )
    async def custom_task():
        pass

    task = get_task("test.custom")
    assert task.description == "A custom task"
    assert task.enabled_by_default is False
    assert task.max_instances == 3
    assert task.misfire_grace_time == 600


def test_get_task_returns_none_for_unknown_key():
    """get_task returns None for unregistered keys."""
    assert get_task("nonexistent") is None


def test_list_tasks_returns_all_registered():
    """list_tasks returns all registered tasks."""

    @register_task(key="test.one", name="One", default_cron="0 * * * *")
    async def task_one():
        pass

    @register_task(key="test.two", name="Two", default_cron="0 * * * *")
    async def task_two():
        pass

    tasks = list_tasks()
    assert len(tasks) == 2
    keys = {t.key for t in tasks}
    assert "test.one" in keys
    assert "test.two" in keys
