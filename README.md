# nytid

Manage TA bookings, schedules, time tracking, task management, GitHub
integration, and agent-assisted task processing.

Example:

```bash
nytid todo start 5
nytid todo note -m "Blocked on student reply"
nytid todo edit --who dbosk
nytid todo done
```

For agent-run tasks, `--run claude` and `--run 'claude -p "..."'` mean
different things: plain `claude` uses the todo's notes or description as
the prompt source, while `claude -p "..."` stores a complete command with
a fixed prompt.

After `nytid todo start 5`, task 5 is on top of the active stack, so
subsequent single-item commands can omit the ID. This shortcut works for
commands such as `nytid todo view`, `nytid todo note`, `nytid todo edit`,
`nytid todo done`, `nytid todo start`, `nytid todo rm`, and
`nytid todo reprioritize`.

For an introduction and overview, read Chapter 1 in the PDF found in the latest 
[release](https://github.com/dbosk/nytid/releases).
