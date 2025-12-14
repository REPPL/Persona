"""Tests for progress tracking (F-075)."""

import time
from datetime import datetime

import pytest

from persona.core.logging.progress import (
    ProgressTracker,
    TaskProgress,
    track_progress,
)


class TestTaskProgress:
    """Tests for TaskProgress dataclass."""

    def test_create_task_progress(self) -> None:
        """Can create a task progress."""
        task = TaskProgress(
            task_id="task-1",
            description="Loading data",
            total=100,
            completed=50,
        )

        assert task.task_id == "task-1"
        assert task.description == "Loading data"
        assert task.total == 100
        assert task.completed == 50

    def test_task_defaults(self) -> None:
        """Task has sensible defaults."""
        task = TaskProgress(
            task_id="task-1",
            description="Test",
        )

        assert task.total == 100
        assert task.completed == 0
        assert task.status == "pending"
        assert task.start_time is None
        assert task.end_time is None
        assert task.subtasks == []

    def test_percent_calculation(self) -> None:
        """Percentage is calculated correctly."""
        task = TaskProgress(
            task_id="task-1",
            description="Test",
            total=200,
            completed=100,
        )

        assert task.percent == 50.0

    def test_percent_with_zero_total(self) -> None:
        """Percentage is 100% when total is 0."""
        task = TaskProgress(
            task_id="task-1",
            description="Test",
            total=0,
            completed=0,
        )

        assert task.percent == 100.0

    def test_elapsed_seconds_not_started(self) -> None:
        """Elapsed is 0 when not started."""
        task = TaskProgress(
            task_id="task-1",
            description="Test",
        )

        assert task.elapsed_seconds == 0.0

    def test_elapsed_seconds_running(self) -> None:
        """Elapsed calculates from start_time."""
        task = TaskProgress(
            task_id="task-1",
            description="Test",
            start_time=datetime.now(),
        )

        # Small sleep to ensure some time passes
        time.sleep(0.1)

        assert task.elapsed_seconds >= 0.1

    def test_eta_seconds_not_started(self) -> None:
        """ETA is None when not started."""
        task = TaskProgress(
            task_id="task-1",
            description="Test",
        )

        assert task.eta_seconds is None

    def test_eta_seconds_zero_completed(self) -> None:
        """ETA is None when nothing completed."""
        task = TaskProgress(
            task_id="task-1",
            description="Test",
            start_time=datetime.now(),
        )

        assert task.eta_seconds is None

    def test_to_dict(self) -> None:
        """Task can be converted to dict."""
        task = TaskProgress(
            task_id="task-1",
            description="Test task",
            total=100,
            completed=25,
            status="running",
        )

        result = task.to_dict()

        assert result["task_id"] == "task-1"
        assert result["description"] == "Test task"
        assert result["total"] == 100
        assert result["completed"] == 25
        assert result["percent"] == 25.0
        assert result["status"] == "running"

    def test_to_dict_includes_subtasks(self) -> None:
        """to_dict includes subtasks."""
        subtask = TaskProgress(
            task_id="sub-1",
            description="Subtask",
        )
        task = TaskProgress(
            task_id="task-1",
            description="Main task",
            subtasks=[subtask],
        )

        result = task.to_dict()

        assert len(result["subtasks"]) == 1
        assert result["subtasks"][0]["task_id"] == "sub-1"


class TestProgressTracker:
    """Tests for ProgressTracker class."""

    def test_create_tracker(self) -> None:
        """Can create a progress tracker."""
        tracker = ProgressTracker(title="Test Progress")

        assert tracker.title == "Test Progress"

    def test_create_tracker_quiet_mode(self) -> None:
        """Can create tracker in quiet mode."""
        tracker = ProgressTracker(quiet=True)

        assert tracker.quiet is True

    def test_add_task(self) -> None:
        """Can add a task to track."""
        tracker = ProgressTracker(quiet=True)

        task_id = tracker.add_task("Loading data", total=100)

        assert task_id is not None
        task = tracker.get_task(task_id)
        assert task is not None
        assert task.description == "Loading data"
        assert task.total == 100

    def test_add_task_with_custom_id(self) -> None:
        """Can add task with custom ID."""
        tracker = ProgressTracker(quiet=True)

        task_id = tracker.add_task("Test", task_id="my-task-id")

        assert task_id == "my-task-id"

    def test_update_task(self) -> None:
        """Can update task progress."""
        tracker = ProgressTracker(quiet=True)
        task_id = tracker.add_task("Test", total=10)

        tracker.update(task_id, advance=3)

        task = tracker.get_task(task_id)
        assert task is not None
        assert task.completed == 3
        assert task.status == "running"

    def test_update_sets_completed_directly(self) -> None:
        """Can set completed value directly."""
        tracker = ProgressTracker(quiet=True)
        task_id = tracker.add_task("Test", total=100)

        tracker.update(task_id, completed=75)

        task = tracker.get_task(task_id)
        assert task is not None
        assert task.completed == 75

    def test_update_changes_description(self) -> None:
        """Can update task description."""
        tracker = ProgressTracker(quiet=True)
        task_id = tracker.add_task("Initial description", total=10)

        tracker.update(task_id, description="Updated description")

        task = tracker.get_task(task_id)
        assert task is not None
        assert task.description == "Updated description"

    def test_update_starts_task(self) -> None:
        """First update starts the task."""
        tracker = ProgressTracker(quiet=True)
        task_id = tracker.add_task("Test", total=10)

        task = tracker.get_task(task_id)
        assert task is not None
        assert task.status == "pending"
        assert task.start_time is None

        tracker.update(task_id, advance=1)

        task = tracker.get_task(task_id)
        assert task is not None
        assert task.status == "running"
        assert task.start_time is not None

    def test_complete_task(self) -> None:
        """Can mark task as complete."""
        tracker = ProgressTracker(quiet=True)
        task_id = tracker.add_task("Test", total=10)
        tracker.update(task_id, advance=5)

        tracker.complete(task_id)

        task = tracker.get_task(task_id)
        assert task is not None
        assert task.status == "completed"
        assert task.completed == task.total
        assert task.end_time is not None

    def test_fail_task(self) -> None:
        """Can mark task as failed."""
        tracker = ProgressTracker(quiet=True)
        task_id = tracker.add_task("Test", total=10)
        tracker.update(task_id, advance=3)

        tracker.fail(task_id, message="Something went wrong")

        task = tracker.get_task(task_id)
        assert task is not None
        assert task.status == "failed"

    def test_get_task_not_found(self) -> None:
        """get_task returns None for unknown task."""
        tracker = ProgressTracker(quiet=True)

        task = tracker.get_task("nonexistent")

        assert task is None

    def test_get_all_tasks(self) -> None:
        """Can get all tasks."""
        tracker = ProgressTracker(quiet=True)
        tracker.add_task("Task 1")
        tracker.add_task("Task 2")
        tracker.add_task("Task 3")

        tasks = tracker.get_all_tasks()

        assert len(tasks) == 3

    def test_subtask_context_manager(self) -> None:
        """Can create subtasks via context manager."""
        tracker = ProgressTracker(quiet=True)
        parent_id = tracker.add_task("Parent task", total=100)

        with tracker.subtask(parent_id, "Subtask 1", total=50) as sub_id:
            tracker.update(sub_id, advance=50)

        parent = tracker.get_task(parent_id)
        assert parent is not None
        assert len(parent.subtasks) == 1
        assert parent.subtasks[0].status == "completed"

    def test_subtask_fails_on_exception(self) -> None:
        """Subtask marked as failed on exception."""
        tracker = ProgressTracker(quiet=True)
        parent_id = tracker.add_task("Parent task")

        with pytest.raises(ValueError):
            with tracker.subtask(parent_id, "Failing subtask") as sub_id:
                raise ValueError("Test error")

        parent = tracker.get_task(parent_id)
        assert parent is not None
        assert len(parent.subtasks) == 1
        assert parent.subtasks[0].status == "failed"

    def test_to_display(self) -> None:
        """Can generate display output."""
        tracker = ProgressTracker(title="Test Progress", quiet=True)
        task_id = tracker.add_task("Test task", total=100)
        tracker.update(task_id, completed=50)

        display = tracker.to_display()

        assert "Test Progress" in display
        assert "Test task" in display
        assert "50%" in display

    def test_context_manager_basic(self) -> None:
        """Tracker works as context manager."""
        with ProgressTracker(quiet=True) as tracker:
            task_id = tracker.add_task("Test", total=10)
            tracker.update(task_id, advance=10)
            tracker.complete(task_id)

    def test_update_nonexistent_task_no_error(self) -> None:
        """Updating nonexistent task doesn't raise error."""
        tracker = ProgressTracker(quiet=True)

        # Should not raise
        tracker.update("nonexistent", advance=1)


class TestTrackProgressConvenience:
    """Tests for track_progress convenience function."""

    def test_iterates_items(self) -> None:
        """track_progress iterates through items."""
        items = [1, 2, 3, 4, 5]
        result = []

        for item in track_progress(items, description="Processing"):
            result.append(item)

        assert result == items

    def test_with_list(self) -> None:
        """Works with list input."""
        result = list(track_progress([1, 2, 3]))
        assert result == [1, 2, 3]

    def test_with_custom_total(self) -> None:
        """Can specify custom total."""
        # Using generator with known total
        def gen():
            yield 1
            yield 2
            yield 3

        result = list(track_progress(gen(), total=3))
        assert result == [1, 2, 3]
