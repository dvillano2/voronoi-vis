.PHONY: run
run:
	uv run main.py

.PHONY: format
format:
	uv run ruff check		
