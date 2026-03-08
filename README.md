# nytid

Manage TA bookings, schedules, time tracking, and task management for teaching.

Example:

```bash
nytid todo start 5
nytid todo note -m "Blocked on student reply"
nytid todo edit --reassign dbosk
nytid todo done
```

After `nytid todo start 5`, task 5 is on top of the active stack, so
subsequent single-item commands can omit the ID. This shortcut works for
commands such as `nytid todo view`, `nytid todo note`, `nytid todo edit`,
`nytid todo done`, `nytid todo start`, `nytid todo rm`, and
`nytid todo reprioritize`.

For an introduction and overview, read Chapter 1 in the PDF found in the latest 
[release](https://github.com/dbosk/nytid/releases).
