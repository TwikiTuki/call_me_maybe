import json
from typing import Any

import pytest
from pydantic import ValidationError

from src.parsing.functions_definitions import (
    FunctionDefinition,
    TypeSpec,
    get_functions_from_string,
)


@pytest.fixture
def definitions() -> list[dict[str, Any]]:
    return [
        {
            "name": "fn_add_numbers",
            "description": "Add two numbers together and return their sum.",
            "parameters": {
                "a": {"type": "number"},
                "b": {"type": "number"},
            },
            "returns": {"type": "number"},
        },
        {
            "name": "fn_greet",
            "description": "Generate a greeting message for a person by name.",
            "parameters": {
                "name": {"type": "string"},
            },
            "returns": {"type": "string"},
        },
    ]


class TestInputDefinitions():
    def test_load_functions(self, definitions: list[dict[str, Any]]) -> None:
        definitions_list = get_functions_from_string(json.dumps(definitions))
        assert len(definitions_list) == 2
        definition = definitions_list[0]
        assert definition.name == 'fn_add_numbers'
        assert isinstance(definition, FunctionDefinition)
        parameters = definition.parameters
        assert len(parameters) == 2
        assert parameters['b']
        assert isinstance(parameters['b'], TypeSpec)
        assert parameters['b'].type == 'number'

        returns = definition.returns
        assert isinstance(returns, TypeSpec)
        assert returns.type == 'number'


def _assert_invalid(definitions: Any) -> None:
    with pytest.raises(ValidationError):
        get_functions_from_string(json.dumps(definitions))


class TestInvalidDefinitions():
    def test_wrong_key_name(self, definitions: list[dict[str, Any]]) -> None:
        definitions[0]['nme'] = definitions[0].pop('name')
        _assert_invalid(definitions)

    def test_missing_returns(self, definitions: list[dict[str, Any]]) -> None:
        del definitions[1]['returns']
        _assert_invalid(definitions)

    def test_wrong_type_key_in_parameter(
            self, definitions: list[dict[str, Any]]) -> None:
        definitions[0]['parameters']['a'] = {'tipe': 'number'}
        _assert_invalid(definitions)

    def test_unknown_parameter_type(
            self, definitions: list[dict[str, Any]]) -> None:
        definitions[0]['parameters']['b']['type'] = 'bool'
        _assert_invalid(definitions)

    def test_unknown_return_type(
            self, definitions: list[dict[str, Any]]) -> None:
        definitions[1]['returns']['type'] = 'integer'
        _assert_invalid(definitions)

    def test_name_not_a_string(
            self, definitions: list[dict[str, Any]]) -> None:
        definitions[0]['name'] = 42
        _assert_invalid(definitions)

    def test_parameters_is_a_list(
            self, definitions: list[dict[str, Any]]) -> None:
        definitions[0]['parameters'] = [{'type': 'number'}]
        _assert_invalid(definitions)

    def test_top_level_not_a_list(
            self, definitions: list[dict[str, Any]]) -> None:
        _assert_invalid(definitions[0])

    def test_invalid_json(self, definitions: list[dict[str, Any]]) -> None:
        with pytest.raises(ValidationError):
            get_functions_from_string(json.dumps(definitions)[:-1])

    def test_extra_key(self, definitions: list[dict[str, Any]]) -> None:
        definitions[0]['fooo'] = ['dooo']
        _assert_invalid(definitions)

    def test_TypeSpec_with_extra(self) -> None:
        with pytest.raises(ValidationError):
            spec: TypeSpec = TypeSpec(**{"type": "string", 'wooo': "koook"})
