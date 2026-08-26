"""Refuse to run the test suite without its configuration sandbox.

`tests/conftest.py` carries the isolation that keeps the whole suite
out of the user's real `typerconf` configuration file.  It is
*generated* from `tests/conftest.nw` by `make -C tests all`, and it is
gitignored, so in a fresh clone -- or in a worktree where somebody
skipped the build -- it is simply absent, and pytest runs happily
without it while every test writes the user's real configuration.
Nothing fails; the damage is silent and outlives the session.

This file is the one place that can notice, because it is the only
pytest hook that exists *before* the build has run.  It is therefore
handwritten and checked in rather than tangled from a `.nw` file: a
guard that has to survive `make` not having run cannot itself be a
build product.  `tests/conftest.nw` explains the reasoning in prose;
this docstring is its summary for whoever opens the `.py`.

pytest loads the conftest files from the rootdir downwards, so this
one is imported before `tests/conftest.py`, and `pytest_configure`
runs after both -- and still before any test module is imported.  That
is exactly the window in which the sandbox can be verified rather than
merely hoped for.
"""

import pathlib

import pytest
import typerconf

REPO_ROOT = pathlib.Path(__file__).parent.resolve()
TESTS_DIR = REPO_ROOT / "tests"
SANDBOX_SOURCE = TESTS_DIR / "conftest.nw"
SANDBOX_MODULE = TESTS_DIR / "conftest.py"

# Read while `typerconf.dirs` still answers truthfully: once
# tests/conftest.py has been imported it reports the sandbox, and the
# question this module asks -- "would a write land in the user's own
# configuration?" -- would answer itself with a yes disguised as a no.
REAL_CONFIG_DIR = pathlib.Path(typerconf.dirs.user_config_dir).resolve()

BUILD_COMMAND = "make -C tests all      # or: cd tests && make test"


def sandbox_module_is_stale():
    """Return a reason string if `tests/conftest.py` needs rebuilding."""
    if not SANDBOX_MODULE.exists():
        return f"{SANDBOX_MODULE} does not exist"
    if not SANDBOX_SOURCE.exists():
        return None
    if SANDBOX_MODULE.stat().st_mtime_ns < SANDBOX_SOURCE.stat().st_mtime_ns:
        return (
            f"{SANDBOX_MODULE} is older than {SANDBOX_SOURCE}"
        )
    return None


def config_writes_escape_the_sandbox():
    """Return a reason string if `typerconf` still points at the user.

    `typerconf` bakes the configuration path into the default
    arguments of `read_config` and `write_config`; those are the exact
    slots `tests/conftest.nw` rewrites, so they are also where the
    redirection can be read back.
    """
    for method in (
        typerconf.Config.read_config,
        typerconf.Config.write_config,
    ):
        defaults = method.__defaults__
        if not defaults:
            continue
        target = pathlib.Path(str(defaults[0])).resolve()
        if target.is_relative_to(REAL_CONFIG_DIR):
            return (
                f"typerconf.Config.{method.__name__} still resolves to "
                f"{target}, the real user configuration"
            )
    return None


def session_targets_the_suite(config):
    """Say whether this pytest session collects `tests/`.

    A session aimed elsewhere in the repository never imports
    `tests/conftest.py`, so the checks below would report a breach
    that cannot happen -- there is nothing to write the configuration.
    """
    if not config.args:
        return True
    for arg in config.args:
        target = pathlib.Path(str(arg).split("::", 1)[0])
        if not target.is_absolute():
            target = config.invocation_params.dir / target
        target = target.resolve()
        if (
            target == TESTS_DIR
            or TESTS_DIR in target.parents
            or target in TESTS_DIR.parents
        ):
            return True
    return False


def pytest_configure(config):
    """Abort the session when the configuration sandbox is not in place."""
    if not session_targets_the_suite(config):
        return

    reason = sandbox_module_is_stale() or config_writes_escape_the_sandbox()
    if reason is None:
        return

    raise pytest.UsageError(
        "the nytid test suite's configuration sandbox is not in effect; "
        "running now would write the real user configuration in "
        f"{REAL_CONFIG_DIR} (typerconf names that directory after "
        "sys.argv[0], which is why it is the test runner's name and not "
        "nytid's).\n"
        f"Reason: {reason}.\n"
        "tests/conftest.py is generated from tests/conftest.nw, and the "
        "root `make all` does not build it.  Build the test tree first:\n"
        f"\n    {BUILD_COMMAND}\n"
    )
