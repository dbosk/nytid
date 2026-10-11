"""TA bookings, schedules, time tracking and task management.

Importing the package honours NYTID_HOME before any nytid module reads
the configuration.  This file is written by hand, not tangled; the
`home` chapter of the manual (src/nytid/home.nw) explains the call.
"""
from nytid.home import apply_nytid_home

apply_nytid_home()
