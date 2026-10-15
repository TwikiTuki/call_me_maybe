import pytest
import torch

from llm_sdk import Small_LLM_Model
from src.response.response import PromptResponse
from src.parsing.functions_definitions import (
    FunctionDefinition,
    get_functions_from_file,
)
from src.parsing.prompts_file import Prompt

FUNCS: list[FunctionDefinition] = get_functions_from_file(
    "data/input/functions_definition.json"
)
NAMES: set[str] = {f.name for f in FUNCS}


# # load the model once for the whole file, not once per test
# @pytest.fixture(scope="module")
# def llm() -> Small_LLM_Model:
#     return Small_LLM_Model(cache_dir="./models", local_files_only=True)


# class TestAddFunction():
#     @pytest.mark.parametrize("text, expected", [
#         ("What is the sum of 2 and 3?", "fn_add_numbers"),
#         ("Greet shrek", "fn_greet"),
#         ("Reverse the string 'hello'", "fn_reverse_string"),
#         ("What is the square root of 16?", "fn_get_square_root"),
#     ])
#     def test_add_function(
#         self, llm: Small_LLM_Model, text: str, expected: str
#     ) -> None:
#         pr = PromptResponse(Prompt(prompt=text), FUNCS, llm)
#         pr.response.openWith('[')
#         pr.response.openWith('{')
#         pr.add_prompt()
#         name: str = pr.add_function()
#         print(pr.response)

#         # always a real function
#         assert name in NAMES
#         # and the right one
#         assert name == expected
#         assert pr.response.content.endswith(f'"name": "{name}",')


class FakeLLM():
    """Each character is one token (its ord). The logits always prefer the
    next character of `wanted`, and '"' once `wanted` is complete, so the
    output is deterministic."""

    VOCAB_SIZE = 256

    def __init__(self, wanted: str):
        self.wanted = wanted

    def encode(self, text: str) -> torch.Tensor:
        return torch.tensor([[ord(c) for c in text]], dtype=torch.long)

    def decode(self, ids: list[int]) -> str:
        return "".join(chr(i) for i in ids)

    def get_logits_from_input_ids(self, input_ids: list[int]) -> list[float]:
        generated: str = self.decode(input_ids).rsplit('"name": "', 1)[-1]
        if len(generated) < len(self.wanted):
            preferred: str = self.wanted[len(generated)]
        else:
            preferred = '"'
        logits: list[float] = [0.0] * self.VOCAB_SIZE
        logits[ord(preferred)] = 10.0
        return logits


def make_function(name: str) -> FunctionDefinition:
    return FunctionDefinition(
        name=name,
        description="",
        parameters={},
        returns={"type": "number"},
    )


def run_add_function(names: list[str], wanted: str) -> tuple[str, str]:
    functions: list[FunctionDefinition] = [make_function(n) for n in names]
    pr = PromptResponse(Prompt(prompt="test"), functions, FakeLLM(wanted))
    pr.response.openWith('[')
    pr.response.openWith('{')
    pr.add_prompt()
    name: str = pr.add_function()
    return name, pr.response.content


class TestAddFunctionFakeLLM():
    NAMES = ["fn_add_numbers", "fn_greet", "fn_reverse_string"]

    @pytest.mark.parametrize("wanted", NAMES)
    def test_returns_wanted_valid_name(self, wanted: str) -> None:
        name, content = run_add_function(self.NAMES, wanted)
        assert name == wanted
        assert content.endswith(f'"name": "{wanted}",')

    def test_unknown_name_is_forced_to_a_valid_one(self) -> None:
        name, content = run_add_function(self.NAMES, "fn_hello")
        assert name in self.NAMES
        assert content.endswith(f'"name": "{name}",')

    def test_cannot_close_before_a_full_name(self) -> None:
        # the fake wants '"' right after "fn_", which is not an entry
        name, _ = run_add_function(self.NAMES, "fn_")
        assert name in self.NAMES

    def test_empty_wanted_cannot_close_immediately(self) -> None:
        name, _ = run_add_function(self.NAMES, "")
        assert name in self.NAMES

    def test_prefix_name_stops_at_short_one(self) -> None:
        names = ["fn_add", "fn_add_numbers"]
        name, content = run_add_function(names, "fn_add")
        assert name == "fn_add"
        assert content.endswith('"name": "fn_add",')

    def test_prefix_name_continues_to_long_one(self) -> None:
        names = ["fn_add", "fn_add_numbers"]
        name, _ = run_add_function(names, "fn_add_numbers")
        assert name == "fn_add_numbers"

    def test_single_function_is_always_chosen(self) -> None:
        name, _ = run_add_function(["fn_greet"], "something_else")
        assert name == "fn_greet"

    def test_no_functions_raises(self) -> None:
        with pytest.raises(ValueError):
            run_add_function([], "fn_greet")
