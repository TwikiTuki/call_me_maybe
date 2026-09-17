import json

import pytest

from src import parser


TEST_FILE_PATHS = {
    'functions_file': 'data/input/functions_definition.json',
    'prompts_default_file': 'data/input/function_calling_tests.json',
    'prompts_file': 'data/input/function_calling_tests_other.json',
    # 'function_calls_default_file': 'data/input/function_calling_tests.json',
    'function_calls_file': 'data/output/function_calls_other.json',
}



@pytest.fixture
def generate_test_files(tmp_path):
    paths = {}
    for name, relative_path in TEST_FILE_PATHS.items():
        path = tmp_path / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps([]))
        paths[name] = path
    return paths

class Test_ProgramArgv():
    def test_default_values(self, generate_test_files):
        parser.ProgramArgv(
            functions_definitions = generate_test_files['functions_file']
        )

    def test_specific_inp_file(self, generate_test_files):
        parser.ProgramArgv(
            functions_definitions = generate_test_files['functions_file'],
            input = generate_test_files['prompts_default_file']
        )

    def test_specific_out_file(self, generate_test_files):
        parser.ProgramArgv(
            functions_definitions = generate_test_files['functions_file'],
            output = generate_test_files['function_calls_file']
        )

    def test_specific_inp_out_files(self, generate_test_files):
        parser.ProgramArgv(
            functions_definitions = generate_test_files['functions_file'],
            input = generate_test_files['prompts_default_file'],
            output = generate_test_files['function_calls_file']
        )

    # def test_with_invalid_params(self):
        #TODO

class Test_argv_to_dict():
    def tesster(self, input, expected):
        res = parser.argv_to_dict(input)
        print(f'res: {res}')
        print(f'expected: {expected}')
        print(f'--------------------------------')
        assert res == expected

    def test_blank(self):
        input = []
        expected= {}
        self.tesster(input, expected)

    def test_with_valid_params(self):
        input = ['--key', 'val']
        expected= {'key': 'val'}
        self.tesster(input, expected)

        input = [ '--key', 'val', '--key2', 'val2', '--key3', 'val3', ]
        expected= { 'key': 'val', 'key2': 'val2', 'key3': 'val3', } 

    # def test_with_invalid_params(self):
        #TODO