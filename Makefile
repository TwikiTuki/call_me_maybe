

install:
	test -d .venv && echo '.venv already exists' || uv venv 
	uv sync 

run:
	uv run python -m src
#	[--functions_definition <function_definition_file>] [--input <input_file>] [-- output <output_file>]

	
debug:
	uv run python -m pdb -m src
	
clean:
	@echo '----- cleaning caches -----'
	find . -type d \( -name '__pycache__' -o -name '.mypy_cache' -o -name '.pytest_cache' -o -name '.ruff_cache' \) -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	
lint:
	@echo '----- mypy   -----'
	uv run mypy . --warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs
	@echo '----- flake8 -----'
	- uv run flake8 .

lint-strict:
	@echo '----- mypy   -----'
	uv run mypy . --strict
	@echo '----- flake8 -----'
	-uv run flake8 .

test:
	uv run pytest
