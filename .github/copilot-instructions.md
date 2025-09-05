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