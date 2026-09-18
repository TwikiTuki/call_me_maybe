import json

import pytest

from pathlib import Path

from src import parser
from typing import Any, cast


TEST_FILE_PATHS: dict[str, str] = {
    'functions_file': 'data/input/functions_definition.json',
    'prompts_default_file': 'data/input/function_calling_tests.json',
    'prompts_file': 'data/input/function_calling_tests_other.json',
    # 'function_calls_default_file': 'data/input/function_calling_tests.json',
    'function_calls_file': 'data/output/function_calls_other.json',
}


type TypeGenerateTestFiles = dict[str, str]

@pytest.fixture
def generate_test_files(tmp_path: Path) -> TypeGenerateTestFiles: # TODO do not use any
    paths: dict[str, str] = {}
    for name, relative_path in TEST_FILE_PATHS.items():
        path: Any = tmp_path / relative_path              # TODO do not use any
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps([]))
        paths[name] = path
    return paths

class Test_ProgramArgv():
    def test_default_values(self, generate_test_files: TypeGenerateTestFiles) -> None:
        parser.ProgramArgv(
            functions_definitions = cast(Path, generate_test_files['functions_file'])
        )
    def test_specific_inp_file(self, generate_test_files: TypeGenerateTestFiles) -> None:
        parser.ProgramArgv(
            functions_definitions=cast(Path, generate_test_files['functions_file']),
            input=cast(Path, generate_test_files['prompts_default_file'])
        )

    def test_specific_out_file(self, generate_test_files: TypeGenerateTestFiles) -> None:
        parser.ProgramArgv(
            functions_definitions=cast(Path, generate_test_files['functions_file']),
            output=cast(Path, generate_test_files['function_calls_file'])
        )

    def test_specific_inp_out_files(self, generate_test_files: TypeGenerateTestFiles) -> None:
        parser.ProgramArgv(
            functions_definitions=cast(Path, generate_test_files['functions_file']),
            input=cast(Path, generate_test_files['prompts_default_file']),
            output=cast(Path, generate_test_files['function_calls_file'])
        )

    # def test_with_invalid_params(self):
        # TODO


class Test_argv_to_dict():
    def tesster(self, input: list[str], expected: dict[str, str]) -> None:
        res = parser.argv_to_dict(input)
        print(f'res: {res}')
        print(f'expected: {expected}')
        print('--------------------------------')
        assert res == expected

    def test_blank(self) -> None:
        input: list[str] = []
        expected: dict[str, str] = {}
        self.tesster(input, expected)

    def test_with_valid_params(self) -> None:
        input: list[str] = ['--key', 'val']
        expected: dict[str, str] = {'key': 'val'}
        self.tesster(input, expected)

        input = ['--key', 'val', '--key2', 'val2', '--key3', 'val3', ]
        expected = {'key': 'val', 'key2': 'val2', 'key3': 'val3', }

    # def test_with_invalid_params(self):
        # TODO
