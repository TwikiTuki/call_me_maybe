

from pathlib import Path

from pydantic import BaseModel, FilePath


class ProgramArgv(BaseModel):
    functions_definitions: FilePath
    input: FilePath = Path('data/input/function_calling_tests.json')
    output: Path = Path('data/output/function_calls.json')

def argv_to_dict(argv: list[str]) -> dict[str, str]:
    print("argv: ")
    print(argv)
    current_param: str | None = None
    params: dict[str, str] = {}
    for arg in argv:
        arg = arg.strip()
        if(arg == ""):
            continue
        if current_param:
            params[current_param] = arg
            current_param = None
        else:
            arg_prefix_slashes = arg[:2]
            assert arg_prefix_slashes == '--' , f"invalid syntax on argument [{arg}]  expected --"
            current_param = arg[2:]
    return params

def parse_arguments(argv: list[str]) -> ProgramArgv:
    print("full argv: ")
    print(argv)
    args_dict: dict = argv_to_dict(argv[1:])
    print("args dict: ")
    print(args_dict)
    return ProgramArgv(**args_dict)
        



