"""Progress tracking with Rich (F-075).

Provides visual progress tracking for long-running operations
with ETA calculation and nested progress support.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterator
from contextlib import contextmanager
import sys


@dataclass
class TaskProgress:
    """Progress information for a single task.

    Attributes:
        task_id: Unique task identifier.
        description: Task description.
        total: Total units of work.
        completed: Completed units of work.
        status: Current status (pending, running, completed, failed).
        start_time: When the task started.
        end_time: When the task ended.
        subtasks: Nested subtasks.
    """
    task_id: str
    description: str
    total: int = 100
    completed: int = 0
    status: str = "pending"
    start_time: datetime | None = None
    end_time: datetime | None = None
    subtasks: list["TaskProgress"] = field(default_factory=list)

    @property
    def percent(self) -> float:
        """Get completion percentage."""
        if self.total == 0:
            return 100.0
        return (self.completed / self.total) * 100

    @property
    def elapsed_seconds(self) -> float:
        """Get elapsed time in seconds."""
        if not self.start_time:
            return 0.0
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()

    @property
    def eta_seconds(self) -> float | None:
        """Estimate time remaining in seconds."""
        if self.completed == 0 or self.total == 0:
            return None
        rate = self.completed / self.elapsed_seconds if self.elapsed_seconds > 0 else 0
        if rate == 0:
            return None
        remaining = self.total - self.completed
        return remaining / rate

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "total": self.total,
            "completed": self.completed,
            "percent": self.percent,
            "status": self.status,
            "elapsed_seconds": self.elapsed_seconds,
            "eta_seconds": self.eta_seconds,
            "subtasks": [s.to_dict() for s in self.subtasks],
        }


class ProgressTracker:
    """Tracker for multi-step workflow progress.

    Provides visual progress bars using Rich library when available,
    with graceful fallback to text output for non-TTY environments.

    Example:
        >>> with ProgressTracker() as progress:
        ...     task = progress.add_task("Loading data", total=3)
        ...     for i in range(3):
        ...         progress.update(task, advance=1)
        ...     progress.complete(task)
    """

    def __init__(
        self,
        title: str = "Progress",
        use_rich: bool = True,
        quiet: bool = False,
    ):
        """Initialise the tracker.

        Args:
            title: Overall progress title.
            use_rich: Use Rich progress bars if available.
            quiet: Suppress all output.
        """
        self.title = title
        self.use_rich = use_rich and self._rich_available()
        self.quiet = quiet

        self._tasks: dict[str, TaskProgress] = {}
        self._task_counter = 0
        self._rich_progress: Any = None
        self._rich_tasks: dict[str, Any] = {}

    def _rich_available(self) -> bool:
        """Check if Rich is available and TTY is attached."""
        try:
            from rich.progress import Progress
            return sys.stdout.isatty()
        except ImportError:
            return False

    def _format_time(self, seconds: float | None) -> str:
        """Format seconds as H:MM:SS."""
        if seconds is None:
            return "--:--"
        mins, secs = divmod(int(seconds), 60)
        hours, mins = divmod(mins, 60)
        if hours:
            return f"{hours}:{mins:02d}:{secs:02d}"
        return f"{mins:02d}:{secs:02d}"

    def add_task(
        self,
        description: str,
        total: int = 100,
        task_id: str | None = None,
    ) -> str:
        """Add a new task to track.

        Args:
            description: Task description.
            total: Total units of work.
            task_id: Optional task ID (auto-generated if not provided).

        Returns:
            Task ID for updates.
        """
        if task_id is None:
            self._task_counter += 1
            task_id = f"task_{self._task_counter}"

        task = TaskProgress(
            task_id=task_id,
            description=description,
            total=total,
            status="pending",
        )
        self._tasks[task_id] = task

        if self.use_rich and self._rich_progress:
            from rich.progress import TaskID
            rich_task = self._rich_progress.add_task(description, total=total)
            self._rich_tasks[task_id] = rich_task

        return task_id

    def update(
        self,
        task_id: str,
        advance: int = 1,
        description: str | None = None,
        completed: int | None = None,
    ) -> None:
        """Update task progress.

        Args:
            task_id: Task to update.
            advance: Units to advance.
            description: New description.
            completed: Set completed to specific value.
        """
        if task_id not in self._tasks:
            return

        task = self._tasks[task_id]

        # Start task if not started
        if task.status == "pending":
            task.status = "running"
            task.start_time = datetime.now()

        # Update completion
        if completed is not None:
            task.completed = completed
        else:
            task.completed += advance

        if description:
            task.description = description

        # Update Rich progress if available
        if self.use_rich and task_id in self._rich_tasks:
            kwargs: dict[str, Any] = {}
            if completed is not None:
                kwargs["completed"] = completed
            else:
                kwargs["advance"] = advance
            if description:
                kwargs["description"] = description
            self._rich_progress.update(self._rich_tasks[task_id], **kwargs)

        # Text fallback output
        elif not self.quiet and not self.use_rich:
            self._print_status(task)

    def complete(self, task_id: str, status: str = "completed") -> None:
        """Mark a task as complete.

        Args:
            task_id: Task to complete.
            status: Final status (completed, failed).
        """
        if task_id not in self._tasks:
            return

        task = self._tasks[task_id]
        task.status = status
        task.completed = task.total
        task.end_time = datetime.now()

        if self.use_rich and task_id in self._rich_tasks:
            self._rich_progress.update(
                self._rich_tasks[task_id],
                completed=task.total,
            )

    def fail(self, task_id: str, message: str = "") -> None:
        """Mark a task as failed.

        Args:
            task_id: Task that failed.
            message: Error message.
        """
        self.complete(task_id, status="failed")
        if message and not self.quiet:
            self._print_text(f"[ERROR] {message}")

    @contextmanager
    def subtask(
        self,
        parent_id: str,
        description: str,
        total: int = 100,
    ) -> Iterator[str]:
        """Create a nested subtask.

        Args:
            parent_id: Parent task ID.
            description: Subtask description.
            total: Total units of work.

        Yields:
            Subtask ID.
        """
        subtask_id = self.add_task(description, total)

        if parent_id in self._tasks:
            parent = self._tasks[parent_id]
            parent.subtasks.append(self._tasks[subtask_id])

        try:
            yield subtask_id
            self.complete(subtask_id)
        except Exception:
            self.fail(subtask_id)
            raise

    def get_task(self, task_id: str) -> TaskProgress | None:
        """Get task progress info.

        Args:
            task_id: Task ID.

        Returns:
            TaskProgress or None if not found.
        """
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> list[TaskProgress]:
        """Get all task progress info."""
        return list(self._tasks.values())

    def _print_text(self, message: str) -> None:
        """Print text to stdout."""
        if not self.quiet:
            print(message)

    def _print_status(self, task: TaskProgress) -> None:
        """Print task status in text format."""
        eta = self._format_time(task.eta_seconds)
        elapsed = self._format_time(task.elapsed_seconds)
        self._print_text(
            f"[INFO] {task.description}... "
            f"({task.completed}/{task.total}) "
            f"[{elapsed} elapsed, ETA {eta}]"
        )

    def to_display(self) -> str:
        """Generate human-readable display."""
        lines = [
            self.title,
            "=" * 50,
            "",
        ]

        for task in self._tasks.values():
            status_icon = {
                "pending": "○",
                "running": "→",
                "completed": "✓",
                "failed": "✗",
            }.get(task.status, "?")

            percent_bar = "━" * int(task.percent / 5) + "─" * (20 - int(task.percent / 5))
            eta = self._format_time(task.eta_seconds)

            lines.append(
                f"{status_icon} {task.description} "
                f"{percent_bar} {task.percent:.0f}% ETA: {eta}"
            )

            for subtask in task.subtasks:
                sub_icon = "✓" if subtask.status == "completed" else "..."
                lines.append(f"  └─ {subtask.description} {sub_icon}")

        return "\n".join(lines)

    def __enter__(self) -> "ProgressTracker":
        """Context manager entry."""
        if self.use_rich:
            try:
                from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn, TimeRemainingColumn
                self._rich_progress = Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TaskProgressColumn(),
                    TimeElapsedColumn(),
                    TimeRemainingColumn(),
                )
                self._rich_progress.start()
            except ImportError:
                self.use_rich = False
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        if self._rich_progress:
            self._rich_progress.stop()


def track_progress(
    iterable: Any,
    description: str = "Processing",
    total: int | None = None,
) -> Iterator[Any]:
    """Convenience generator for tracking iteration progress.

    Args:
        iterable: Items to iterate.
        description: Progress description.
        total: Total items (auto-detected if possible).

    Yields:
        Items from iterable.
    """
    items = list(iterable) if total is None else iterable
    total = len(items) if total is None else total

    with ProgressTracker() as tracker:
        task_id = tracker.add_task(description, total=total)
        for item in items:
            yield item
            tracker.update(task_id, advance=1)
        tracker.complete(task_id)
