# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

nytid is a Python CLI application for managing TA bookings, lab sessions, tutorials, course schedules, time tracking, and task management. It uses literate programming (noweb) to generate Python source code from `.nw` files, Poetry for dependency management, and integrates with Canvas LMS and LADOK systems.

## Build & Test Commands

**CRITICAL**: Execute these commands in order. NEVER CANCEL any build commands.

```bash
# 1. Initialize git submodules (REQUIRED - contains build system)
git submodule update --init --recursive

# 2. Install system dependencies
sudo apt-get update && sudo apt-get install -y noweb

# 3. Install Poetry and Python dependencies
pip3 install poetry
poetry install

# 4. Install black code formatter in Poetry environment
poetry run pip install black

# 5. Build source files from noweb literate programming files
make all  # Generates Python files from .nw files using notangle, formats with black

# 6. Run tests
cd tests && make test  # Expected: 14/24 tests pass (failures due to missing Canvas/LADOK/AFS)

# 7. Run the CLI
poetry run nytid --help
```

**Commonly used commands:**
- `make clean && make all` — Clean rebuild of all generated files
- `cd tests && make test` — Run full test suite
- `cd tests && poetry run pytest test_courses.py -v` — Run a single test file
- `cd tests && poetry run pytest test_courses.py::test_function_name -v` — Run a single test function
- `cd tests && poetry run pytest -k "keyword" -v` — Run tests matching a keyword

## Architecture

### CLI Auto-Discovery

The entry point is `nytid.cli:cli` (defined in `pyproject.toml`). The CLI module (`src/nytid/cli/__init__.py`, generated from `init.nw`) dynamically discovers and loads all sibling Python modules in the `cli/` package. Each CLI module (courses, schedule, hr, todo, track, etc.) exports a `cli` Typer instance which gets registered as a subcommand group automatically. To add a new CLI subcommand group, create a new `.nw` file in `src/nytid/cli/` that defines a `cli = typer.Typer(...)` and register the generated `.py` file in `src/nytid/cli/Makefile` under `MODULES`.

### Build System (Cascading Makefiles)

The build uses a git submodule (`makefiles/`) providing `noweb.mk` and `subdir.mk`:
- `subdir.mk` recurses into directories listed in `SUBDIR` for goals listed in `SUBDIR_GOALS`
- `noweb.mk` provides rules to tangle `.nw` → `.py` (via `notangle`) and weave `.nw` → `.tex` (via `noweave`), then formats Python with `black`
- Each subdirectory has its own `Makefile` declaring `MODULES` (generated `.py` files) and `SUBDIR` (child directories)
- The build cascades: root `Makefile` → `src/nytid/Makefile` → `cli/Makefile`, `storage/Makefile`, etc.

### Generated vs Handwritten Files

**Almost all `.py` files are generated from `.nw` files** — including `cli/__init__.py` (from `init.nw`). The `.gitignore` lists all generated paths. The only handwritten Python files are:
- `src/nytid/__init__.py` (empty package marker)
- `src/nytid/signup/__init__.py`
- `src/nytid/signup/hr/timesheet/__init__.py`
- `src/nytid/httputils.py` (legacy, being replaced by `http_utils.nw`)

### Documentation and Source Relationship

`doc/nytid.tex` is the main document that `\input`s the `.tex` files woven from each `.nw` source file. **When adding a new `.nw` file in `src/`, you must also add a corresponding `\input{../src/...}` line in `doc/nytid.tex`**, otherwise it won't appear in the built documentation.

The document is organized into parts mirroring the source tree:
- Part I "The CLI" — `src/nytid/cli/*.tex`
- Part II "Storage" — `src/nytid/storage/*.tex`
- Part III "Managing courses" — `src/nytid/courses/*.tex`
- Part IV "Core library" — `src/nytid/schedules.tex`, `src/nytid/signup/*.tex`

**Keep these three descriptions in sync** — they all describe what nytid is and does:
- `doc/abstract.tex` — LaTeX abstract for the PDF documentation
- `README.md` — GitHub project description
- `src/nytid/cli/init.nw` — the `<<nytid description>>` chunk (becomes the CLI `--help` text)

### Module Layers

```
CLI layer (src/nytid/cli/)     → Typer commands, user-facing interface
  ↓ uses
Library layer (src/nytid/)     → schedules.nw, courses/, signup/, storage/
  ↓ integrates with
External services              → Canvas LMS, LADOK, AFS
```

## Literate Programming

This project uses literate programming (noweb) with two fundamental goals:
1. **Explain to human beings what we want a computer to do** — Write for human readers
2. **Present concepts in psychological order** — Introduce ideas when easiest to understand, not when the compiler needs them

### Core Principles

- **Explain the "why"** — If you find yourself writing code comments to explain logic, that explanation belongs in the documentation chunks instead
- **Write documentation first** — Start with explanation, then add code
- **Keep lines under 80 characters** — Both in documentation and code chunks
- **Use meaningful chunk names** — Describe purpose like pseudocode (2-5 words)
- **Decompose by concept** — Break code into chunks based on logical units
- **Never commit generated files** — Only commit .nw files; .py and .tex files are build artifacts

### Noweb File Format

```noweb
This is documentation explaining what we're doing.
We'll implement [[factorial]] function.

<<factorial.py>>=
"""Module docstring"""
<<imports>>
<<factorial function>>
@

The factorial function uses recursion:
<<factorial function>>=
def factorial(n):
    """Compute n factorial."""
    <<base case>>
    return n * factorial(n - 1)
@

For the base case:
<<base case>>=
if n <= 1:
    return 1
@
```

### Variation Theory Structure

Structure literate programs using variation theory patterns:
- **Start with the whole** — Present the complete picture first
- **Use contrast** — Show what something IS vs what it is NOT
- **Examine parts** — Break down and explain each component
- **Reassemble** — Show how parts work together

### Progressive Disclosure with Chunk Concatenation

Use abstract placeholder chunks to defer implementation details:

```noweb
def cli_show(user_regex,
             <<options for filtering>>):
  """Shows contracts."""
  <<implementation>>
@

[... 300 lines later, explaining each option ...]

\paragraph{The [[--all]] option}
<<options for filtering>>=
all: bool = False,
@

\paragraph{The [[--next]] option}
<<options for filtering>>=
next: bool = False
@
```

### Chunk Dependency Hazard

When a code chunk is defined in multiple concatenated blocks (e.g., `<<options for filtering>>` above), every code path that uses values from those blocks must appear AFTER all the blocks. If implementation code references a variable set in a later concatenation block, `notangle` will produce code where the variable is used before it's defined — causing `UnboundLocalError` at runtime.

### Test Organization

Tests should appear AFTER the functionality they verify:

```noweb
\section{Feature Implementation}
<<implementation>>=
def feature_x():
    # implementation
@

Now let's verify this works:
<<test functions>>=
def test_feature_x():
    assert feature_x() == expected
@
```

### Workflow for Modifying .nw Files

1. **Read the existing file** to understand current structure and narrative
2. **Plan with literate programming in mind** — What is the "why"? How does it fit the narrative?
3. **Design documentation BEFORE writing code**
4. **Decompose code into well-named chunks**
5. **Regenerate with `make all` and test**

## LaTeX Best Practices

Documentation chunks in .nw files are LaTeX. Follow these practices:

### Semantic Markup

Use LaTeX environments that match semantic meaning:

**Use `description` for term-definition pairs:**
```latex
\begin{description}
\item[Configuration] Set timeout to 30 seconds
\item[Performance] Optimized for large datasets
\end{description}
```

**NOT:**
```latex
\begin{itemize}
\item \textbf{Configuration:} Set timeout...  % WRONG
\end{itemize}
```

### Code References in .nw Files

Use `[[code]]` notation, NOT `\texttt{...\_...}`:

```latex
% CORRECT
The [[get_submission()]] method calls [[__getattribute__]].

% INCORRECT - manual escaping
The \texttt{get\_submission()} method calls \texttt{\_\_getattribute\_\_}.
```

### Cross-References

Always use `\cref{...}` (cleveref), never manual prefixes:

```latex
% CORRECT
\cref{sec:intro} shows...

% INCORRECT
Section~\ref{sec:intro} shows...
```

### Quotations

Always use `\enquote{...}`, never manual quote marks:

```latex
% CORRECT
\enquote{This is a quote}

% INCORRECT
"This is a quote"
``This is a quote''
```

### Emphasis

Never use ALL CAPITALS for emphasis. Use `\emph{...}`:

```latex
% CORRECT
This is \emph{very} important.

% INCORRECT
This is VERY important.
```

### Figures with sidecaption (memoir class)

```latex
\begin{figure}
  \begin{sidecaption}{Description}[fig:label]
    \includegraphics[width=0.7\textwidth]{path/to/image}
  \end{sidecaption}
\end{figure}
```

## Git Commit Practices

**CRITICAL: Commit early, commit often, one concern per commit!**

### Atomic Commits

Each commit should represent ONE logical change that can be understood, reviewed, and reverted independently.

### When to Commit

Commit immediately after:
- Fixing a single bug
- Completing a logical unit
- Refactoring one aspect
- Adding one feature component
- Updating documentation

### Branch Safety

- **NEVER** commit directly to `main` or `master`
- **ALWAYS** work on a feature/topic branch
- Check current branch before committing: `git branch --show-current`

### Commit Message Format

```
Short summary (50 chars or less, imperative mood)

Optional detailed explanation:
- What changed
- Why it changed

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Literate Programming Projects

In this project, **NEVER commit generated files**:

```bash
# GOOD - only commit .nw source
git add src/module.nw
git commit -m "Add new feature to module"

# BAD - never commit generated files
git add src/module.py   # Generated from .nw - DO NOT COMMIT
```

## Troubleshooting

### Build Issues
- **"No rule to make target 'makefiles/subdir.mk'"**: Run `git submodule update --init --recursive`
- **"black: not found"**: Run `poetry run pip install black`
- **Python import errors**: Run `make all` to generate Python files from .nw sources

### Test Failures
- Canvas/LADOK credential failures: Expected in development environments
- AFS permission errors: Expected when AFS is not available

### CLI Warnings
- Syntax warnings about invalid escape sequences: Non-critical
- Canvas/LADOK credential warnings: Expected for fresh installations

## Integration Points

- **Canvas LMS**: Requires `canvaslms login` for Canvas integration
- **LADOK**: Requires `ladok login` for student system integration
- **AFS**: Andrew File System for secure storage (optional)
