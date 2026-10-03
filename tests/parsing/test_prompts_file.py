import copy
import json
from typing import Any

import pytest
from pydantic import ValidationError

from src.parsing.prompts_file import (
    Prompt,
    get_prompts_from_string,
)

prompts_inp: list[dict[str: str]] = [
  {
    "prompt": "What is the sum of 2 and 3?"
  },
  {
    "prompt": "What is the sum of 265 and 345?"
  },
  {
    "prompt": "Greet shrek"
  },
  {
    "prompt": "Greet john"
  },
  {
    "prompt": "Reverse the string 'hello'"
  },
]

prompts_str = json.dumps(prompts_inp)

class TestPrompts():
    def test_get_prompts_from_string(self):
        prompts_list = get_prompts_from_string(prompts_str)
        assert type(prompts_list) == list
        assert len(prompts_list) == len(prompts_inp)
        prompt:Prompt = prompts_list[0]
        assert type(prompt) == Prompt 
        assert prompt.prompt == prompt.prompt


def _assert_invalid(prompts: Any) -> None:
    with pytest.raises(ValidationError):
        get_prompts_from_string(json.dumps(prompts))


class TestInvalidPrompts():
    def test_wrong_key_name(self) -> None:
        prompts = copy.deepcopy(prompts_inp)
        prompts[0]['promt'] = prompts[0].pop('prompt')
        _assert_invalid(prompts)

    def test_missing_prompt_key(self) -> None:
        prompts = copy.deepcopy(prompts_inp)
        prompts[2] = {}
        _assert_invalid(prompts)

    def test_prompt_not_a_string(self) -> None:
        prompts = copy.deepcopy(prompts_inp)
        prompts[1]['prompt'] = 42
        _assert_invalid(prompts)

    def test_prompt_is_null(self) -> None:
        prompts = copy.deepcopy(prompts_inp)
        prompts[1]['prompt'] = None
        _assert_invalid(prompts)

    def test_list_of_strings(self) -> None:
        prompts = [p['prompt'] for p in prompts_inp]
        _assert_invalid(prompts)

    def test_top_level_not_a_list(self) -> None:
        prompts = copy.deepcopy(prompts_inp)
        _assert_invalid(prompts[0])

    def test_invalid_json(self) -> None:
        with pytest.raises(ValidationError):
            get_prompts_from_string('[{"prompt": "Greet shrek"')

    # @pytest.mark.xfail(reason="extra keys are ignored until extra='forbid'")
    def test_extra_key(self) -> None:
        prompts = copy.deepcopy(prompts_inp)
        prompts[0]['foo'] = 1
        _assert_invalid(prompts)

