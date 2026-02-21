# Installation

## Requirements

- Python 3.10 or higher
- pip

## Install from PyPI

```bash
pip install nl-clicalc
```

## Install from Source

```bash
git clone https://github.com/dbowman91/nl-clicalc.git
cd nl-clicalc
pip install -e .
```

## Development Installation

For contributing or development:

```bash
git clone https://github.com/dbowman91/nl-clicalc.git
cd nl-clicalc
pip install -e ".[dev]"
pre-commit install
```

## Verify Installation

```bash
calc --version
# calc 1.1.0

calc "one plus one"
# 1+1 -> 2
```

## Shell Completions

### Bash

Add to `~/.bashrc`:

```bash
source /path/to/nl-clicalc/completions/calc.bash
```

### Zsh

Copy to your fpath:

```bash
cp completions/_calc ~/.zsh/completions/
```

Or add to `~/.zshrc`:

```bash
fpath=(/path/to/nl-clicalc/completions $fpath)
```

### Fish

Copy to Fish completions directory:

```bash
cp completions/calc.fish ~/.config/fish/completions/
```

## Man Page

Install the man page:

```bash
cp docs/nl-clicalc.1 /usr/local/share/man/man1/
man calc
```
