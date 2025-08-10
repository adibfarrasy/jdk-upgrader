default:
    @just --list

install:
    pip install -r requirements.txt

format:
    ruff format .

lint:
    ruff check .

run path:
    python main.py {{path}}

dry-run path:
    python main.py {{path}} --dry-run

auto path:
    python main.py {{path}} --auto-approve

clean:
    find . -type d -name __pycache__ -delete
    find . -name "*.pyc" -delete


# collect TODOs across the entire codebase
note:
    @echo "Compiling notes..."
    @echo "TODOs:" > TODOs.md
    @if ! grep -rn -H --exclude-dir=target --exclude-dir=.git "# TODO" src | sed 's/^/\t/' | sed 's/:[[:space:]]*#[[:space:]]*TODO:[[:space:]]*/:\t/' >> TODOs.md 2>/dev/null; then echo "N/A" >> TODOs.md; fi
