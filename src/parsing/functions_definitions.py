from typing import Literal
from pydantic import BaseModel, ConfigDict, FilePath, TypeAdapter

type LlmType = Literal["number", "string"]

# TODO Really needed or could just work with LlmType?
class TypeSpec(BaseModel):
    model_config = ConfigDict(extra='forbid')
    type: LlmType


class FunctionDefinition(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str
    description: str
    parameters: dict[str, TypeSpec]
    returns: TypeSpec


_FunctionList = TypeAdapter(list[FunctionDefinition])


def get_functions_from_string(text: str) -> list[FunctionDefinition]:
    return _FunctionList.validate_json(text)


def get_functions_from_file(file: FilePath) -> list[FunctionDefinition]:
    with open(file) as f:
        return get_functions_from_string(f.read())
