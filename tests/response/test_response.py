import pytest
import torch

from llm_sdk import Small_LLM_Model
from typing import get_args

from random import random

from src.response.response import (
    PICKER_BY_TYPE,
    IntPicker,
    PromptResponse,
    QuotedStringPicker,
    StringPicker,
)
from src.parsing.functions_definitions import (
    FunctionDefinition,
    LlmType,
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
    """Each character is one token (its ord). The logits prefer the next
    character of `wanted`, then '"' once `wanted` is complete, and a random
    character on the calls after that."""

    VOCAB_SIZE = 256

    def __init__(self, wanted: str):
        self.wanted = wanted
        self.current = 0

    @classmethod
    def _encode(cls, text: str) -> torch.Tensor:
        return torch.tensor([[ord(c) for c in text]], dtype=torch.long)

    @classmethod
    def single_token(cls, text: str) -> int:
        """Token id of a single-token text."""
        tokens: list[int] = cls._encode(text).tolist()[0]
        return tokens[0]

    def encode(self, text: str) -> torch.Tensor:
        return self._encode(text)

    @classmethod
    def _decode(cls, ids: list[int]) -> str:
        return "".join(chr(i) for i in ids)

    def decode(self, ids: list[int]) -> str:
        return self._decode(ids)

    def get_logits_from_input_ids(self, input_ids: list[int]) -> list[float]:
        # each call generates one token, so current is the index of the next one
        if self.current < len(self.wanted):
            preferred: str = self.wanted[self.current]
        elif self.current == len(self.wanted):
            preferred = '"'
        else:
            preferred = FakeLLM._decode([int(random() * self.VOCAB_SIZE)])   # TODO maybe puting random thing on a test is not best practice. Could create a string of random chars and use that with modulus

        self.current += 1
        logits: list[float] = [0.0] * self.VOCAB_SIZE
        logits[self.single_token(preferred)] = 10.0
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
    name: str = pr.add_function_name()
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


class TestGenerateResponseFakeLLM():
    NAMES = ["fn_add_numbers", "fn_greet", "fn_reverse_string"]

    def make_response(self, wanted: str, prompt: str = "test") -> PromptResponse:
        functions: list[FunctionDefinition] = [
            make_function(n) for n in self.NAMES
        ]
        return PromptResponse(Prompt(prompt=prompt), functions, FakeLLM(wanted))

    def test_returns_the_built_content(self) -> None:
        pr = self.make_response("fn_greet")
        result: str = pr.generate_response()
        assert result == pr.response.content

    def test_starts_with_the_instruction(self) -> None:
        pr = self.make_response("fn_greet")
        instruction: str = pr.generate_init_instruction(pr.prompt)
        assert pr.generate_response().startswith(instruction)

    # @pytest.mark.parametrize("wanted", NAMES)
    # def test_generated_json_part(self, wanted: str) -> None:
    #     pr = self.make_response(wanted, prompt="Greet shrek")
    #     instruction: str = pr.generate_init_instruction(pr.prompt)
    #     generated: str = pr.generate_response()[len(instruction):]
    #     # TODO: once add_arguments is implemented the trailing ',' after
    #     # "name" is followed by "parameters" and this becomes valid json
    #     assert generated == (
    #         '['
    #         '\n {'
    #         '\n  "prompt": "Greet shrek",'
    #         f'\n  "name": "{wanted}",'
    #         '\n }'
    #         '\n]'
    #     )

    def test_indent_is_back_to_zero(self) -> None:
        pr = self.make_response("fn_greet")
        pr.generate_response()
        assert pr.response.indent == 0

    def test_unknown_name_is_forced_to_a_valid_one(self) -> None:
        pr = self.make_response("fn_hello")
        generated: str = pr.generate_response()
        last_name: str = generated.rsplit('"name": "', 1)[-1].split('"', 1)[0]
        assert last_name in self.NAMES


def prefer(*chars: str) -> list[float]:
    """Logits where the given chars are the most likely, in that order."""
    logits: list[float] = [0.0] * FakeLLM.VOCAB_SIZE
    for i, c in enumerate(chars):
        logits[FakeLLM.single_token(c)] = 10.0 - i
    return logits


class TestIntPicker():
    def test_pick_logit(self) -> None:
        picker = IntPicker(FakeLLM(""))  # type: ignore[arg-type]

        # cannot end before generating anything
        assert picker.pick_logit(prefer(',', '-')) == FakeLLM.single_token('-')

        # cannot end or put another '-' right after '-'
        assert picker.pick_logit(prefer(',', '-', '4')) == FakeLLM.single_token('4')

        # non digit tokens are ignored
        assert picker.pick_logit(prefer('a', '.', '2')) == FakeLLM.single_token('2')

        # '-' is only allowed at the start
        assert picker.pick_logit(prefer('-', '7')) == FakeLLM.single_token('7')

        # ends once at least one digit was generated
        assert picker.pick_logit(prefer(',')) is None

    def test_custom_end_token(self) -> None:
        picker = IntPicker(FakeLLM(""), end_token='}')  # type: ignore[arg-type]
        assert picker.pick_logit(prefer('1')) == FakeLLM.single_token('1')

        # ',' is not the end token anymore so it is ignored
        assert picker.pick_logit(prefer(',', '3')) == FakeLLM.single_token('3')
        assert picker.pick_logit(prefer('}')) is None

    def test_max_tokens(self) -> None:
        picker = IntPicker(FakeLLM(""), max_tokens=2)  # type: ignore[arg-type]
        assert picker.pick_logit(prefer('1')) == FakeLLM.single_token('1')
        assert picker.pick_logit(prefer('2')) == FakeLLM.single_token('2')

        # stops even though the model still wants digits
        assert picker.pick_logit(prefer('3')) is None


class TestStringPicker():
    def test_pick_logit(self) -> None:
        picker = StringPicker(FakeLLM(""))  # type: ignore[arg-type]
        assert picker.pick_logit(prefer('h')) == FakeLLM.single_token('h')
        assert picker.pick_logit(prefer(' ')) == FakeLLM.single_token(' ')

        # tokens that would break the json string are skipped
        assert picker.pick_logit(prefer('\\', '\n', 'i')) == FakeLLM.single_token('i')

        # the end token stops the generation
        assert picker.pick_logit(prefer('"')) is None

    def test_custom_end_token(self) -> None:
        picker = StringPicker(FakeLLM(""), end_token="'")  # type: ignore[arg-type]

        # '"' is still forbidden even when it is not the end token
        assert picker.pick_logit(prefer('"', 'x')) == FakeLLM.single_token('x')
        assert picker.pick_logit(prefer("'")) is None

    def test_max_tokens(self) -> None:
        picker = StringPicker(FakeLLM(""), max_tokens=2)  # type: ignore[arg-type]
        assert picker.pick_logit(prefer('a')) == FakeLLM.single_token('a')
        assert picker.pick_logit(prefer('b')) == FakeLLM.single_token('b')

        # stops even though the model still wants letters
        assert picker.pick_logit(prefer('c')) is None

    def test_no_valid_tokens_raises(self) -> None:
        picker = StringPicker(FakeLLM(""))  # type: ignore[arg-type]
        with pytest.raises(ValueError):
            picker.pick_logit([])


class TestQuotedStringPicker():
    def test_pick_logit(self) -> None:
        picker = QuotedStringPicker(FakeLLM(""))  # type: ignore[arg-type]

        # the first token is always the opening quote
        assert picker.pick_logit(prefer('a')) == FakeLLM.single_token('"')

        # then it works like a StringPicker
        assert picker.pick_logit(prefer('h')) == FakeLLM.single_token('h')
        assert picker.pick_logit(prefer('\\', 'i')) == FakeLLM.single_token('i')

        # when the string ends the closing quote is returned
        assert picker.pick_logit(prefer('"')) == FakeLLM.single_token('"')

        # and after that the generation stops
        assert picker.pick_logit(prefer('x')) is None

    def test_max_tokens_still_closes_the_string(self) -> None:
        picker = QuotedStringPicker(FakeLLM(""), max_tokens=1)  # type: ignore[arg-type]
        assert picker.pick_logit(prefer('a')) == FakeLLM.single_token('"')
        assert picker.pick_logit(prefer('a')) == FakeLLM.single_token('a')

        # the limit is reached but the string is closed anyway
        assert picker.pick_logit(prefer('a')) == FakeLLM.single_token('"')
        assert picker.pick_logit(prefer('a')) is None


class TestPickerByType():
    def test_mapping(self) -> None:
        # every LlmType has a picker
        assert set(PICKER_BY_TYPE) == set(get_args(LlmType.__value__))
        assert PICKER_BY_TYPE["number"] is IntPicker
        assert PICKER_BY_TYPE["string"] is QuotedStringPicker

        # the pickers can be built from the mapping with an end token
        picker = PICKER_BY_TYPE["number"](FakeLLM(""), '}')  # type: ignore[arg-type]
        assert isinstance(picker, IntPicker)
        assert picker.end_token == FakeLLM.single_token('}')
