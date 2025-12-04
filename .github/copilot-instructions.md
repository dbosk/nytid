# nytid - Teaching Assistant Management System

nytid is a Python CLI application for managing TA bookings, lab sessions, tutorials, and course schedules. It uses literate programming (noweb) to generate Python source code from `.nw` files, Poetry for dependency management, and integrates with Canvas LMS and LADOK systems.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Bootstrap, Build, and Test the Repository

**CRITICAL**: Execute these commands in order. NEVER CANCEL any build commands - they may take several minutes but are essential.

```bash
# 1. Initialize git submodules (REQUIRED - contains build system)
git submodule update --init --recursive

# 2. Install system dependencies
sudo apt-get update && sudo apt-get install -y noweb

# 3. Install Poetry (Python dependency manager)
pip3 install poetry
export PATH=$HOME/.local/bin:$PATH

# 4. Install Python dependencies
poetry install  # Takes ~30 seconds

# 5. Install black code formatter in Poetry environment
poetry run pip install black
# If pip install fails due to network timeout, try again or use system package:
# sudo apt-get install -y python3-black && export PATH=/usr/bin:$PATH

# 6. Build source files from noweb literate programming files
export PATH=$HOME/.cache/pypoetry/virtualenvs/*/bin:$PATH
make all  # Takes ~4 seconds. NEVER CANCEL. Set timeout to 10+ minutes.
```

**Expected Build Output**: Build generates Python files from `.nw` files using `notangle` and formats them with `black`. Documentation generation will fail due to missing `inkscape` but this is expected and does not affect functionality.

### Run Tests

```bash
cd tests
make test  # Takes ~2 seconds. NEVER CANCEL. Set timeout to 5+ minutes.
```

**Expected Test Results**: 14/24 tests pass. Failures are expected in container environments due to missing Canvas/LADOK credentials and AFS (Andrew File System) dependencies.

### Run the Application

```bash
# Basic CLI usage
export PATH=$HOME/.local/bin:$PATH
poetry run nytid --help

# Test main commands
poetry run nytid courses --help
poetry run nytid schedule --help
poetry run nytid signupsheets --help
poetry run nytid hr --help
poetry run nytid utils --help
```

**Application Status**: CLI is fully functional. Warnings about Canvas/LADOK credentials are expected for fresh installations.

## Validation

- **ALWAYS** run the complete bootstrap sequence when working with a fresh clone.
- **MANUAL VALIDATION REQUIREMENT**: After any changes to `.nw` files, rebuild with `make all` and test CLI functionality with `poetry run nytid --help`.
- **NEVER CANCEL builds or tests** - they complete quickly but timeouts should be generous.
- Always run `make clean` before rebuilding if you encounter build issues.

## Build System Details

### Architecture
- **Source Format**: Literate programming using noweb (`.nw` files)
- **Generated Code**: Python files (`.py`) created by `notangle`
- **Code Formatting**: Automatic formatting with `black`
- **Dependencies**: Managed by Poetry (`pyproject.toml`)
- **Build Tool**: GNU Make with custom makefiles

### Critical Dependencies
- `noweb` (notangle, noweave): Literate programming tools
- `poetry`: Python dependency management
- `black`: Code formatter (must be in PATH during build)
- Git submodules: `makefiles/` and `doc/didactic/`

### Build Timing
- **Git submodule init**: ~5 seconds
- **Poetry install**: ~30 seconds
- **Source generation**: ~4 seconds
- **Tests**: ~2 seconds
- **Poetry build**: ~1 second

## Literate Programming Best Practices

### Core Philosophy

This project uses literate programming (noweb) with two fundamental goals:

1. **Explain to human beings what we want a computer to do** - Write for human readers, not just compilers
2. **Present concepts in psychological order** - Introduce ideas when they're easiest to understand, not when the compiler needs them

**Key principle:** Explain the "why" behind the code, not just the "what". If you find yourself writing code comments to explain logic, that explanation belongs in the documentation chunks instead.

### Variation Theory Integration

Structure literate programs using variation theory patterns:

- **Start with the whole** - Present the complete picture first
- **Use contrast** - Highlight key concepts by showing what they're NOT (old vs new approaches, correct vs incorrect)
- **Examine parts** - Break down and explain each component
- **Reassemble** - Show how parts work together

### Planning Changes to .nw Files

**CRITICAL:** Before modifying any .nw file, follow this process:

1. **Read the existing file** to understand current structure and narrative
2. **Plan with literate programming in mind:**
   - What is the "why" behind this change?
   - How does it fit into the existing narrative?
   - Should I use contrast to explain the change?
   - What new chunks are needed? What are their meaningful names?
   - Where in the pedagogical order should this be explained?
3. **Design documentation BEFORE writing code:**
   - Write prose explaining the problem and solution
   - Use subsections to structure complex explanations
   - Provide examples showing the new behavior
   - Explain design decisions and trade-offs
4. **Decompose code into well-named chunks:**
   - Each chunk = one coherent concept
   - Names describe purpose (like pseudocode), not syntax
   - Use 2-5 word summaries of chunk purpose
5. **Write the code chunks referenced in documentation**
6. **Regenerate with `make all` and test**

### Chunk Naming Best Practices

- **Meaningful names**: Describe what the code does, not its syntactic role
- **Like pseudocode**: "validate user input" not "check function"
- **2-5 words**: Brief but descriptive summaries
- **Purpose-focused**: "parse configuration file" not "config code"

**Examples:**
```noweb
<<parse command line arguments>>=
<<validate user input>>=
<<fetch data from Canvas API>>=
<<calculate grade statistics>>=
```

### Line Length Guidelines

**Keep lines under 80 characters** in both documentation and code chunks:

- **Documentation prose**: Break at natural points (end of sentences, after commas)
- **Python code**: Use implicit string concatenation, parentheses for expressions
- **Why**: Improves readability, follows Unix conventions, works well in side-by-side diffs

**Note:** Black formatter may reformat to different lengths, but keep .nw source readable.

### Code Formatting Integration

Use black formatter on generated Python files:

```bash
# Format during build
notangle -Rfile.py file.nw | black - > file.py

# Or format after generation
make all  # Already integrates black via makefiles
```

### Writing Quality Literate Programs

1. **Write documentation first** - Start with explanation, then add code
2. **Use meaningful chunk names** - Describe purpose like pseudocode
3. **Decompose by concept** - Break code by logical units, not syntax
4. **Explain the "why"** - Don't just describe what code does (that's visible)
5. **Keep chunks focused** - One chunk = one coherent idea
6. **Use web structure** - Define chunks out of order when pedagogically helpful
7. **Maintain line discipline** - Keep under 80 characters for readability

### Literate Programming Review Checklist

When reviewing .nw files, check:

- [ ] **Narrative flow**: Does the document tell a coherent story?
- [ ] **Pedagogical order**: Are concepts presented for human understanding, not compiler requirements?
- [ ] **Variation theory**: Are contrasts used to highlight key concepts?
- [ ] **Chunk quality**: Meaningful names? Appropriate size? Single concepts?
- [ ] **Explanation quality**: "Why" explained, not just "what"? Design decisions documented?
- [ ] **Line length**: Both prose and code under 80 characters?
- [ ] **Proper noweb syntax**: Correct `[[code]]` references? Valid chunk definitions?
- [ ] **No unused chunks**: Run `noroots` to find typos in chunk names

### Version Control for Literate Programs

- **Commit only .nw files** - Never commit generated .py files
- **Keep generated code in .gitignore** - The .nw file is the source of truth
- **Regenerate before testing** - Always run `make all` after modifying .nw files

## LaTeX Writing Best Practices

This project generates documentation from .nw files to LaTeX. Follow these practices for high-quality LaTeX output.

### Core Principle: Semantic Markup

Use LaTeX environments that match the **semantic meaning** of content, not just visual appearance. LaTeX is a document preparation system based on describing what content *is*, not how it should *look*.

### List Environments

Choose the right environment for the content structure:

#### Use `description` for Term-Definition Pairs

When you have labels followed by explanations, definitions, or descriptions:

```latex
\begin{description}
\item[Configuration] Set timeout to 30 seconds
\item[Performance] Optimized for large datasets
\item[username] The user's login name
\end{description}
```

**Common use cases:** API parameters, configuration options, glossary entries, feature descriptions.

**Anti-pattern to avoid:**
```latex
% INCORRECT - Don't do this
\begin{itemize}
\item \textbf{Configuration:} Set timeout to 30 seconds
\item \textbf{Performance:} Optimized for large datasets
\end{itemize}
```

#### Use `itemize` for Simple Lists

When items are uniform list elements without labels:

```latex
\begin{itemize}
\item First uniform item
\item Second uniform item
\end{itemize}
```

#### Use `enumerate` for Numbered Steps

When order matters (sequential steps, rankings):

```latex
\begin{enumerate}
\item First step in the process
\item Second step in the process
\end{enumerate}
```

### Quotations: Always Use csquotes

**Always** use `\enquote{...}` for quotes, never manual quote marks:

```latex
% CORRECT
\enquote{This is a quote}
\enquote{outer \enquote{inner} quote}

% INCORRECT - Don't use manual quotes
"This is a quote"
``This is a quote''
```

**Why:** Manual quote marks don't adapt to language settings. The csquotes package handles all quote styling correctly based on document language (Swedish uses »...«, English uses "...").

For block quotes, use `\begin{displayquote}...\end{displayquote}`

### Emphasis: Never Use ALL CAPITALS

**Never** use ALL CAPITALS for emphasis in running text. Use `\emph{...}` instead:

```latex
% CORRECT
This is \emph{very} important to understand.
The \emph{benefits} of classes are clear.

% INCORRECT - Don't do this
This is VERY important to understand.
The BENEFITS of classes are clear.
```

**Why:** ALL CAPITALS in running text is considered shouting and poor typography. It's harder to read and looks unprofessional. Let LaTeX handle emphasis semantically.

**Exception:** Acronyms and proper names conventionally written in capitals (NASA, USA, PDF) are fine.

### Figures and Tables

**Core principle:** An image is not a figure, but a figure can contain an image. Always use proper figure/table environments with captions and labels.

#### Using sidecaption (memoir class)

This project uses the memoir document class. Prefer `sidecaption` over traditional `\caption`:

```latex
% For figures
\begin{figure}
  \begin{sidecaption}{Clear description of image content}[fig:label]
    \includegraphics[width=0.7\textwidth]{path/to/image}
  \end{sidecaption}
\end{figure}

% For tables
\begin{table}
  \begin{sidecaption}{Description of table content}[tab:label]
    \begin{tabular}{lcc}
      \toprule
      Header1 & Header2 & Header3 \\
      \midrule
      Data1 & Data2 & Data3 \\
      \bottomrule
    \end{tabular}
  \end{sidecaption}
\end{table}
```

**Benefits:** Caption appears alongside content, better space efficiency, improved readability, clear semantic separation.

#### Referencing figures and tables

Always use `\cref{fig:label}` (cleveref package) or `\ref{fig:label}`:

```latex
As shown in \cref{fig:memory-hierarchy}, secondary memory is slower.
The results in \cref{tab:benchmark} demonstrate...
```

**Never** hard-code "Figure 1" or "Table 3.2"—let LaTeX handle numbering automatically.

### Beamer: Presentation vs Article Mode

When creating Beamer presentations that also generate article versions, use `\mode<presentation>` and `\mode<article>`:

```latex
\begin{frame}
  \mode<presentation>{%
    \begin{remark}[Key Point]
      \begin{itemize}
        \item Concise point 1
        \item Concise point 2
      \end{itemize}
    \end{remark}
  }
  \mode<article>{%
    \begin{remark}[Key Point]
      Full explanatory paragraph with detailed reasoning and context
      that would overwhelm a slide but provides value in written form.
    \end{remark}
  }
\end{frame}
```

**Principle:** Slides need visual clarity and conciseness (bullets, short phrases). Articles provide depth and explanation (full sentences, paragraphs).

### LaTeX Review Checklist

When reviewing LaTeX code in .nw files, check:

- [ ] Lists using `\textbf{Label:}` instead of `description` environment?
- [ ] Hard-coded numbers instead of `\ref`/`\cref`?
- [ ] Manual quotes (`"..."`, `'...'`) instead of `\enquote{...}`?
- [ ] ALL CAPITALS for emphasis instead of `\emph{...}`?
- [ ] Images without `figure` environment and captions?
- [ ] Hard-coded "Figure 1" instead of `\cref{fig:label}`?
- [ ] Windows-style backslashes in paths? (Use forward slashes)

## Git Commit Practices

**CRITICAL: Commit early, commit often, one concern per commit!**

This project follows atomic commit practices to maintain clean, reviewable git history.

### Core Principle: Atomic Commits

Each commit should represent **one logical change** - a single fix, feature, or refactoring that can be understood, reviewed, and reverted independently.

**Benefits:**
- Easier code review (understand one change at a time)
- Safer reverts (undo specific changes without losing other work)
- Clearer history (git log tells the project story)
- Better debugging (git bisect works effectively)

### Branch Safety: Always Use Feature Branches

**NEVER commit directly to `main` or `master` branches.** Always work on a feature/topic branch:

```bash
# Check current branch
git branch --show-current

# If on main/master, create feature branch
git checkout -b fix-authentication-bug

# Branch naming: descriptive, hyphenated
# Good: fix-auth-bug, add-export-feature, refactor-authentication
# Bad: fix1, updates, wip
```

### When to Commit

**✅ Commit immediately after:**

1. **Fixing a single bug** - One bug, one commit
2. **Completing a logical unit** - Function works, tests pass
3. **Refactoring one aspect** - Before and after are both working states
4. **Adding one feature component** - Each independent piece
5. **Updating documentation** - Separate from code changes
6. **Making configuration changes** - Isolated from feature work
7. **Completing a todo item** - One item = one commit

**❌ Don't wait until:**

- You've fixed "everything"
- The entire feature is complete
- You've changed many files
- End of the day/session

### Commit Granularity Examples

**Bad (too large):**
```
✗ "Fix critical bugs in grading scripts"
  - Fixed 3 different bugs in 5 files
  - Cannot review changes independently
```

**Good (atomic):**
```
✓ Commit 1: "Fix terminal grading timestamp format mismatch"
✓ Commit 2: "Fix LaTeX grading undefined variable reference"
✓ Commit 3: "Fix SSH command injection in common.sh"
✓ Commit 4: "Quote variables in common.sh for safety"
✓ Commit 5: "Quote variables in git grading script"
```

Each commit is independently reviewable and revertable.

### Commit Message Format

```
Short summary (50 chars or less)

Optional detailed explanation:
- What changed
- Why it changed
- Impact or implications

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Summary line rules:**

- **Imperative mood**: "Fix bug" not "Fixed bug" or "Fixes bug"
- **Capitalize first word**: "Add feature" not "add feature"
- **No period at end**: "Update docs" not "Update docs."
- **Be specific**: "Fix timestamp mismatch in terminal grading" not "Fix bug"

**Examples:**

```
✓ "Fix timestamp format mismatch in terminal grading"
✓ "Add error handling for missing Canvas credentials"
✓ "Quote variables in common.sh for space safety"
✓ "Refactor course parsing to use dataclasses"

✗ "Fix stuff"
✗ "Updates"
✗ "WIP"
✗ "Fixed various issues"
```

### Workflow for Multiple Changes

When fixing multiple issues:

1. **Fix the first issue**
   ```bash
   vim file1.nw
   make all  # verify it works
   git add file1.nw
   git commit -m "Fix specific issue in file1"
   ```

2. **Fix the second issue**
   ```bash
   vim file2.nw
   make all
   git add file2.nw
   git commit -m "Fix specific issue in file2"
   ```

3. **Never batch multiple fixes** - Each commit should be independently reviewable

### Red Flags: Stop and Commit Now

Watch for these signs you should commit immediately:

1. **Multiple file changes** - 3+ modified files likely means multiple concerns
2. **Large diffs** - Long `git diff` output should be broken up
3. **Mixed concerns** - If commit message needs "and", split it
4. **Time passing** - 15+ minutes since last commit
5. **Task switching** - Always commit before starting new work
6. **Working state reached** - When you think "that works", commit it

### Pre-Commit Checklist

Before each commit, verify:

- [ ] **On correct branch** - Not on main/master (unless explicitly approved)
- [ ] **One logical change** - Single fix, feature, or refactoring
- [ ] **Clear message** - Describes what changed specifically
- [ ] **All related changes included** - Nothing missing
- [ ] **No unrelated changes** - Nothing extra
- [ ] **Code works at this commit** - Tests pass (if applicable)
- [ ] **Can be understood independently** - Reviewable on its own

### Integration with .nw Files

After modifying .nw files:

```bash
# Edit the .nw file
vim module.nw

# Regenerate code
make all

# Commit ONLY the .nw file (generated code is in .gitignore)
git add module.nw
git commit -m "Add input validation to module"
```

**Never commit generated .py files** - they're regenerated from .nw sources.

### Recovery from Large Commits

If you've already made a large commit with multiple concerns (not ideal):

**Option 1: Accept and learn** - Don't rewrite if already pushed

**Option 2: Split before pushing**
```bash
# Reset to before the commit
git reset HEAD~1

# Stage and commit each logical piece separately
git add -p file.nw
git commit -m "First logical change"

git add -p file.nw
git commit -m "Second logical change"
```

### Remember: Working State → Commit → Continue

**The mantra:** Commit early and often. Each working state should be captured in a commit. This makes the project history a clear story of development, not a series of large, opaque changes.

## Common Tasks

### Repository Structure

```
nytid/
├── src/nytid/           # Source code (literate programming .nw files)
│   ├── cli/             # Command-line interface modules
│   ├── courses/         # Course management
│   ├── signup/          # Sign-up sheet management
│   ├── storage/         # Storage backends (AFS)
│   └── schedules.nw     # Schedule handling
├── tests/               # Test suite (generates from .nw files)
├── doc/                 # Documentation (LaTeX/PDF generation)
├── makefiles/           # Build system (git submodule)
├── pyproject.toml       # Poetry configuration
└── poetry.lock          # Dependency lock file
```

### Key Commands Reference

```bash
# Clean and rebuild everything
make clean && make all

# Build Python package
poetry build

# Run specific CLI commands
poetry run nytid courses ls              # List courses
poetry run nytid schedule show           # Show schedules  
poetry run nytid utils rooms             # Find free rooms
poetry run nytid config --help           # Configuration management

# Development workflow
make clean                               # Clean generated files
git submodule update --init --recursive  # Update submodules
poetry install                          # Install/update dependencies
make all                                # Generate source code
cd tests && make test                    # Run test suite
```

### Integration Points
- **Canvas LMS**: Requires `canvaslms login` for Canvas integration
- **LADOK**: Requires `ladok login` for student system integration  
- **AFS**: Andrew File System for secure storage (optional)

### Documentation
- **PDF Manual**: Available in latest GitHub releases (`nytid.pdf`)
- **Source Documentation**: Generated from `.nw` files to LaTeX/PDF
- **CLI Help**: All commands have built-in `--help` documentation

## Troubleshooting

### Build Issues
- **"No rule to make target 'makefiles/subdir.mk'"**: Run `git submodule update --init --recursive`
- **"black: not found"**: Install black in Poetry environment: `poetry run pip install black`
- **Python import errors**: Run `make all` to generate Python files from .nw sources
- **Poetry not found**: Install and add to PATH: `pip3 install poetry && export PATH=$HOME/.local/bin:$PATH`

### Test Failures
- Canvas/LADOK credential failures: Expected in development environments
- AFS permission errors: Expected when AFS is not available
- Course registry errors: Expected when no courses are configured

### CLI Warnings
- Syntax warnings about invalid escape sequences: Non-critical, do not affect functionality
- Canvas/LADOK credential warnings: Expected for fresh installations

### Performance Notes
- Source generation is fast (~4 seconds) but set generous timeouts
- Most operations complete in seconds, not minutes
- Documentation generation may fail due to missing LaTeX/Inkscape dependencies (non-critical)

**NEVER CANCEL builds or long-running commands** - they typically complete quickly but infrastructure delays can occur.