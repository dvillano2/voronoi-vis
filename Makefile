.PHONY: run
run:
	uv run main.py

.PHONY: fix
format:
	uv run ruff check && uv run ruff format
