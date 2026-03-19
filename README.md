# nytid

A CLI and library for managing TA bookings, course schedules, sign-up sheets,
employment contracts, time tracking, and task management. Every interactive
workflow has a scriptable equivalent, so repetitive tasks can be handed off to
Cron or AI agents.

## Command overview

### `courses` — manage course registries and configurations

Maintain a set of course registries (directories of course data), add or remove
courses, and configure per-course settings such as Canvas URLs and TimeEdit ICS
links.

```bash
nytid courses ls
nytid courses new DD1310
nytid courses config DD1310
```

### `schedule` — view and export combined schedules

Display a unified schedule that merges course events, external ICS calendars,
and pending tasks. Export the result as an ICS file for import into any calendar
application.

```bash
nytid schedule show
nytid schedule ics > schedule.ics
nytid schedule external add https://cloud.timeedit.net/…
```

### `signupsheets` — generate TA sign-up sheets

Generate CSV sign-up sheets from the course schedule so that TAs can indicate
which lab sessions they want to work. The sheets are designed for Google Sheets.

```bash
nytid signupsheets generate DD1310
nytid signupsheets set_url DD1310 https://docs.google.com/…
```

### `hr` — employment contracts and time sheets

Compute employment data from completed sign-up sheets: generate amanuensis
contracts, produce time sheets for hourly-employed TAs, and summarize hours per
course.

```bash
nytid hr amanuensis create DD1310
nytid hr timesheets generate DD1310
nytid hr time DD1310
```

### `track` — track time on activities

Track time spent on course activities with free-form labels. Start a label
directly, or launch a command or tmux shell from the same entry point. View
statistics, export to JSON/CSV/ICS, and edit past entries.

```bash
nytid track start DD1310 grading
nytid track start email --run mutt
nytid track stop
nytid track stats
```

### `todo` — task management with agent support

Priority-based task list with working-directory capture, notes, and GitHub issue
sync. Tasks can be started interactively or handed off to AI agents in headless
mode. The schedule view automatically slots pending tasks into free time.

```bash
nytid todo add "Grade assignment 3" --prio 2
nytid todo ls
nytid todo start 5
nytid todo done
nytid todo sync
```

### `utils` — room availability and other utilities

```bash
nytid utils rooms set-url https://… "Sal A" "Sal B"
```

## Quick start

```bash
pip install nytid
nytid courses registry add kth ~/courses
nytid courses new DD1310
nytid schedule show
```

## Documentation

For a full introduction and design overview, read the PDF found in the latest
[release](https://github.com/dbosk/nytid/releases).
