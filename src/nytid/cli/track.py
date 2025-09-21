import datetime
import json
import logging
import os
import pathlib
import sys
import subprocess
import typer
from typing_extensions import Annotated
from typing import List, Optional
import time


DEFAULT_TRACKING_DIR = pathlib.Path.home() / ".nytid" / "tracking"
TRACKING_DATA_FILE = DEFAULT_TRACKING_DIR / "tracking_data.json"
CURRENT_SESSION_FILE = DEFAULT_TRACKING_DIR / "current_session.json"

cli = typer.Typer(name="track", help="Track time spent on course activities")


def format_duration(duration: datetime.timedelta) -> str:
    """Format a duration in a human-readable way"""
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def get_labels_display(labels: List[str]) -> str:
    """Get a display string for labels"""
    return " > ".join(labels) if labels else "No labels"


class TrackingEntry:
    """Represents a single time tracking entry"""

    def __init__(
        self,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        labels: List[str],
        description: str = "",
    ):
        self.start_time = start_time
        self.end_time = end_time
        self.labels = labels
        self.description = description

    def duration(self) -> datetime.timedelta:
        """Get the duration of this tracking entry"""
        return self.end_time - self.start_time

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "labels": self.labels,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TrackingEntry":
        """Create from dictionary (JSON deserialization)"""
        return cls(
            start_time=datetime.datetime.fromisoformat(data["start_time"]),
            end_time=datetime.datetime.fromisoformat(data["end_time"]),
            labels=data["labels"],
            description=data.get("description", ""),
        )


class ActiveSession:
    """Represents an active tracking session"""

    def __init__(self):
        self.label_stack: List[tuple] = []  # (label, start_time) pairs

    def push_labels(self, labels: List[str], start_time: datetime.datetime):
        """Add new labels to the tracking stack"""
        for label in labels:
            self.label_stack.append((label, start_time))

    def pop_labels(self, count: int = 1) -> List[TrackingEntry]:
        """Remove labels from stack and return completed entries"""
        if not self.label_stack:
            return []

        end_time = datetime.datetime.now()
        entries = []

        for _ in range(min(count, len(self.label_stack))):
            if self.label_stack:
                label, start_time = self.label_stack.pop()
                # Create labels list from current stack + the popped label
                current_labels = [l for l, _ in self.label_stack] + [label]
                entries.append(TrackingEntry(start_time, end_time, current_labels))

        return entries

    def clear_all(self) -> List[TrackingEntry]:
        """Clear all labels and return completed entries"""
        return self.pop_labels(len(self.label_stack))

    def get_current_labels(self) -> List[str]:
        """Get the current active labels"""
        return [label for label, _ in self.label_stack]

    def is_active(self) -> bool:
        """Check if there are any active tracking labels"""
        return len(self.label_stack) > 0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "label_stack": [
                (label, start_time.isoformat())
                for label, start_time in self.label_stack
            ]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ActiveSession":
        """Create from dictionary (JSON deserialization)"""
        session = cls()
        session.label_stack = [
            (label, datetime.datetime.fromisoformat(start_time))
            for label, start_time in data.get("label_stack", [])
        ]
        return session


def ensure_tracking_dir():
    """Ensure the tracking directory exists"""
    DEFAULT_TRACKING_DIR.mkdir(parents=True, exist_ok=True)


def load_tracking_data() -> List[TrackingEntry]:
    """Load tracking data from file"""
    if not TRACKING_DATA_FILE.exists():
        return []

    try:
        with open(TRACKING_DATA_FILE, "r") as f:
            data = json.load(f)
            return [TrackingEntry.from_dict(entry) for entry in data]
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logging.warning(f"Error loading tracking data: {e}")
        return []


def save_tracking_data(entries: List[TrackingEntry]):
    """Save tracking data to file"""
    ensure_tracking_dir()
    with open(TRACKING_DATA_FILE, "w") as f:
        json.dump([entry.to_dict() for entry in entries], f, indent=2)


def load_active_session() -> ActiveSession:
    """Load active session from file"""
    if not CURRENT_SESSION_FILE.exists():
        return ActiveSession()

    try:
        with open(CURRENT_SESSION_FILE, "r") as f:
            data = json.load(f)
            return ActiveSession.from_dict(data)
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logging.warning(f"Error loading active session: {e}")
        return ActiveSession()


def save_active_session(session: ActiveSession):
    """Save active session to file"""
    ensure_tracking_dir()
    with open(CURRENT_SESSION_FILE, "w") as f:
        json.dump(session.to_dict(), f, indent=2)


def add_completed_entries(new_entries: List[TrackingEntry]):
    """Add completed entries to tracking data"""
    if not new_entries:
        return

    existing_entries = load_tracking_data()
    existing_entries.extend(new_entries)
    save_tracking_data(existing_entries)


@cli.command()
def start(
    labels: List[str] = typer.Argument(..., help="Labels to track (can be nested)"),
    offset_minutes: Optional[int] = typer.Option(
        None,
        "--offset",
        "-o",
        help="Offset start time by this many minutes (negative for past)",
    ),
):
    """
    Start tracking time with the given labels.
    Labels are nested, so 'DD1310 lecture' creates a hierarchy.
    Running start again adds new labels to the current tracking.
    """
    if not labels:
        typer.echo("Error: At least one label is required", err=True)
        raise typer.Exit(1)

    # Calculate start time with offset
    start_time = datetime.datetime.now()
    if offset_minutes is not None:
        start_time += datetime.timedelta(minutes=offset_minutes)

    # Load current session
    session = load_active_session()

    # Add new labels to the session
    session.push_labels(labels, start_time)

    # Save session
    save_active_session(session)

    # Display current status
    current_labels = session.get_current_labels()
    typer.echo(f"Started tracking: {get_labels_display(current_labels)}")
    if offset_minutes is not None:
        typer.echo(
            f"Start time offset by {offset_minutes} minutes: {start_time.strftime('%H:%M:%S')}"
        )


@cli.command()
def stop(
    all_labels: bool = typer.Option(
        False, "--all", "-a", help="Stop tracking for all active labels"
    ),
    offset_minutes: Optional[int] = typer.Option(
        None,
        "--offset",
        "-o",
        help="Offset stop time by this many minutes (negative for past)",
    ),
):
    """
    Stop tracking. By default stops the most recently started labels.
    Use --all to stop all active tracking.
    """
    session = load_active_session()

    if not session.is_active():
        typer.echo("No active tracking session", err=True)
        raise typer.Exit(1)

    # Calculate end time with offset
    end_time = datetime.datetime.now()
    if offset_minutes is not None:
        end_time += datetime.timedelta(minutes=offset_minutes)
        # Update the session's label times if we're offsetting
        for i, (label, start_time) in enumerate(session.label_stack):
            session.label_stack[i] = (label, start_time)

    # Stop tracking and get completed entries
    if all_labels:
        completed_entries = session.clear_all()
        save_active_session(ActiveSession())  # Clear the session
        typer.echo("Stopped all tracking")
    else:
        completed_entries = session.pop_labels(1)
        save_active_session(session)
        if session.is_active():
            typer.echo(
                f"Stopped latest label. Still tracking: {get_labels_display(session.get_current_labels())}"
            )
        else:
            typer.echo("Stopped tracking")

    # Update end times if offset was provided
    if offset_minutes is not None and completed_entries:
        for entry in completed_entries:
            entry.end_time = end_time

    # Save completed entries
    add_completed_entries(completed_entries)

    # Display what was completed
    for entry in completed_entries:
        typer.echo(
            f"Completed: {get_labels_display(entry.labels)} ({format_duration(entry.duration())})"
        )


@cli.command()
def status():
    """
    Show current tracking status.
    """
    session = load_active_session()

    if not session.is_active():
        typer.echo("No active tracking")
        return

    typer.echo("Currently tracking:")
    current_time = datetime.datetime.now()

    for i, (label, start_time) in enumerate(session.label_stack):
        duration = current_time - start_time
        indent = "  " * i
        typer.echo(f"{indent}- {label} (for {format_duration(duration)})")

    total_labels = session.get_current_labels()
    typer.echo(f"\nFull label hierarchy: {get_labels_display(total_labels)}")


@cli.command()
def run(
    command_args: List[str] = typer.Argument(..., help="Command and arguments to run"),
    labels: List[str] = typer.Option(
        [], "--label", "-l", help="Labels for this tracking session"
    ),
):
    """
    Run a command and track the time spent.
    The command should be provided as arguments after the labels.
    """
    if not command_args:
        typer.echo("Error: Command is required", err=True)
        raise typer.Exit(1)

    if not labels:
        # Use the command as a label if no labels provided
        labels = [command_args[0]]

    start_time = datetime.datetime.now()

    # Load current session and add labels
    session = load_active_session()
    session.push_labels(labels, start_time)
    save_active_session(session)

    typer.echo(
        f"Running '{' '.join(command_args)}' and tracking as: {get_labels_display(labels)}"
    )

    try:
        # Run the command
        result = subprocess.run(command_args, capture_output=False)
        exit_code = result.returncode
    except KeyboardInterrupt:
        typer.echo("\nCommand interrupted", err=True)
        exit_code = 130
    except FileNotFoundError:
        typer.echo(f"Command not found: {command_args[0]}", err=True)
        exit_code = 127

    # Stop tracking and save the completed entry
    end_time = datetime.datetime.now()
    completed_entries = session.pop_labels(len(labels))

    # Update end times
    for entry in completed_entries:
        entry.end_time = end_time

    # Save state
    save_active_session(session)
    add_completed_entries(completed_entries)

    duration = end_time - start_time
    typer.echo(f"Command completed in {format_duration(duration)}")

    raise typer.Exit(exit_code)


@cli.command()
def add(
    labels: List[str] = typer.Argument(..., help="Labels for the time entry"),
    duration_minutes: int = typer.Option(
        ..., "--duration", "-d", help="Duration in minutes"
    ),
    start_offset_minutes: int = typer.Option(
        0,
        "--start-offset",
        help="Start time offset in minutes from now (negative for past)",
    ),
    description: str = typer.Option(
        "", "--description", help="Description for this time entry"
    ),
):
    """
    Add a time entry for work done when not at the computer.
    Useful for recording time spent in meetings, at whiteboards, etc.
    """
    if not labels:
        typer.echo("Error: At least one label is required", err=True)
        raise typer.Exit(1)

    if duration_minutes <= 0:
        typer.echo("Error: Duration must be positive", err=True)
        raise typer.Exit(1)

    # Calculate times
    now = datetime.datetime.now()
    start_time = now + datetime.timedelta(minutes=start_offset_minutes)
    end_time = start_time + datetime.timedelta(minutes=duration_minutes)

    # Create and save entry
    entry = TrackingEntry(start_time, end_time, labels, description)
    add_completed_entries([entry])

    typer.echo(
        f"Added entry: {get_labels_display(labels)} ({format_duration(entry.duration())})"
    )
    if description:
        typer.echo(f"Description: {description}")
    typer.echo(f"Time: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")


@cli.command()
def stats(
    days: int = typer.Option(7, "--days", help="Number of days to include in stats"),
    weekly_limit: float = typer.Option(
        40.0, "--weekly-limit", help="Weekly hour limit for warnings"
    ),
    daily_limit: float = typer.Option(
        8.0, "--daily-limit", help="Daily hour limit for warnings"
    ),
):
    """
    Show statistics about tracked time.
    """
    entries = load_tracking_data()

    if not entries:
        typer.echo("No tracking data available")
        return

    now = datetime.datetime.now()
    cutoff_date = now - datetime.timedelta(days=days)

    # Filter entries within the time range
    recent_entries = [e for e in entries if e.start_time >= cutoff_date]

    if not recent_entries:
        typer.echo(f"No tracking data in the last {days} days")
        return

    # Calculate totals
    total_time = sum((e.duration() for e in recent_entries), datetime.timedelta())
    total_hours = total_time.total_seconds() / 3600

    typer.echo(f"Statistics for the last {days} days:")
    typer.echo(f"Total time: {format_duration(total_time)} ({total_hours:.1f} hours)")
    typer.echo(f"Average per day: {total_hours/days:.1f} hours")

    # Check against limits
    if total_hours > (weekly_limit * days / 7):
        typer.echo(
            f"⚠️  Warning: Exceeding weekly limit of {weekly_limit} hours per week",
            err=True,
        )

    # Daily breakdown
    typer.echo(f"\nDaily breakdown:")
    daily_totals = {}
    for entry in recent_entries:
        date = entry.start_time.date()
        if date not in daily_totals:
            daily_totals[date] = datetime.timedelta()
        daily_totals[date] += entry.duration()

    for date in sorted(daily_totals.keys(), reverse=True):
        duration = daily_totals[date]
        hours = duration.total_seconds() / 3600
        warning = " ⚠️" if hours > daily_limit else ""
        typer.echo(f"  {date}: {format_duration(duration)} ({hours:.1f}h){warning}")

    # Label breakdown
    typer.echo(f"\nTime by top-level labels:")
    label_totals = {}
    for entry in recent_entries:
        if entry.labels:
            top_label = entry.labels[0]
            if top_label not in label_totals:
                label_totals[top_label] = datetime.timedelta()
            label_totals[top_label] += entry.duration()

    for label, duration in sorted(
        label_totals.items(), key=lambda x: x[1], reverse=True
    ):
        hours = duration.total_seconds() / 3600
        percentage = (duration.total_seconds() / total_time.total_seconds()) * 100
        typer.echo(
            f"  {label}: {format_duration(duration)} ({hours:.1f}h, {percentage:.1f}%)"
        )


@cli.command()
def export(
    format: str = typer.Option(
        "ics", "--format", "-f", help="Export format (ics, json, csv)"
    ),
    days: int = typer.Option(30, "--days", help="Number of days to export"),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file (stdout if not specified)"
    ),
):
    """
    Export tracking data in various formats.
    Supports ICS (calendar), JSON, and CSV formats.
    """
    entries = load_tracking_data()

    if not entries:
        typer.echo("No tracking data to export", err=True)
        return

    # Filter by date range
    now = datetime.datetime.now()
    cutoff_date = now - datetime.timedelta(days=days)
    filtered_entries = [e for e in entries if e.start_time >= cutoff_date]

    if not filtered_entries:
        typer.echo(f"No tracking data in the last {days} days", err=True)
        return

    # Generate export data
    if format.lower() == "ics":
        export_data = export_to_ics(filtered_entries)
    elif format.lower() == "json":
        export_data = export_to_json(filtered_entries)
    elif format.lower() == "csv":
        export_data = export_to_csv(filtered_entries)
    else:
        typer.echo(f"Unsupported format: {format}", err=True)
        raise typer.Exit(1)

    # Output to file or stdout
    if output:
        with open(output, "w") as f:
            f.write(export_data)
        typer.echo(f"Exported {len(filtered_entries)} entries to {output}")
    else:
        print(export_data)


def export_to_ics(entries: List[TrackingEntry]) -> str:
    """Export entries to ICS format"""
    try:
        import ics.icalendar
        import ics.event
    except ImportError:
        typer.echo("ICS export requires the 'ics' package", err=True)
        raise typer.Exit(1)

    calendar = ics.icalendar.Calendar()

    for entry in entries:
        event = ics.event.Event()
        event.name = f"Work: {get_labels_display(entry.labels)}"
        event.begin = entry.start_time
        event.end = entry.end_time

        if entry.description:
            event.description = entry.description

        # Add labels as categories
        if entry.labels:
            event.categories = set(entry.labels)

        calendar.events.add(event)

    return str(calendar)


def export_to_json(entries: List[TrackingEntry]) -> str:
    """Export entries to JSON format"""
    return json.dumps([entry.to_dict() for entry in entries], indent=2)


def export_to_csv(entries: List[TrackingEntry]) -> str:
    """Export entries to CSV format"""
    import io
    import csv

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(
        ["Start Time", "End Time", "Duration (minutes)", "Labels", "Description"]
    )

    # Write entries
    for entry in entries:
        duration_minutes = entry.duration().total_seconds() / 60
        labels_str = " > ".join(entry.labels)
        writer.writerow(
            [
                entry.start_time.isoformat(),
                entry.end_time.isoformat(),
                f"{duration_minutes:.1f}",
                labels_str,
                entry.description,
            ]
        )

    return output.getvalue()
