from pydantic import BaseModel, ConfigDict, FilePath, TypeAdapter

# TODO claude is talking about a generic from _*List adapters


class Prompt(BaseModel):
    model_config = ConfigDict(extra='forbid')

    prompt: str


_PromptList = TypeAdapter(list[Prompt])


def get_prompts_from_string(text: str) -> list[Prompt]:
    return _PromptList.validate_json(text)


def get_prompts_from_file(file: FilePath) -> list[Prompt]:
    with open(file) as f:
        return get_prompts_from_string(f.read())
