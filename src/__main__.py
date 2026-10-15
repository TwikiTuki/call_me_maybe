print("hellow from src/__main__.py")    # TODO delte
import traceback
from src.parsing.arguments import parse_arguments, ProgramArgv
from src.parsing.functions_definitions import get_functions_from_file, FunctionDefinition
from src.parsing.prompts_file import get_prompts_from_file, Prompt
from src.response.response import PromptResponse
from src.util.token_tree import TokenNode, print_tree
from sys import argv
from llm_sdk import Small_LLM_Model
from math import inf



def load_data(arguments: ProgramArgv) -> tuple[list[FunctionDefinition], list[Prompt]] | None:
    print("Loading function definitions")
    try:
        function_definitions: list[FunctionDefinition] = get_functions_from_file(
            arguments.functions_definitions
        )   
    except Exception as e:
        print(" :::: Something whent wrong while loading the functions definitions :::")
        traceback.print_exception(e)
        return None
    print("Loading prompts")
    try:
        prompts: list[Prompt] = get_prompts_from_file(arguments.input)
    except Exception as e:
        print(" :::: Something whent wrong while loading the prompts :::")
        traceback.print_exception(e)
        return None
    print("Cheking output file")
    try:
        if arguments.output.is_dir():
            raise IsADirectoryError(
                f"output path [{arguments.output}] is a directory"
            )
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        with open(arguments.output, "a"):
            pass
    except Exception as e:
        print(" :::: Something whent wrong while checking the output file ::::")
        traceback.print_exception(e)
        return None

    return function_definitions, prompts


def __main__() -> None:
    print("Parsing arguments")
    try:
        arguments: ProgramArgv = parse_arguments(argv)
    except Exception as e:
        print(" :::: Something whent wrong while parsing the input parameters ::::")
        traceback.print_exception(e)
        return

    dta: None | tuple[list[FunctionDefinition], list[Prompt]] = load_data(arguments)
    if not dta:
        return
    function_definitions: list[FunctionDefinition]
    prompts: list[Prompt]
    function_definitions, prompts = dta
    llm: Small_LLM_Model = Small_LLM_Model(cache_dir="./models", local_files_only=True)              # I is using the local option llm model
    for p in prompts:
        # p.prompt = '"give me this string but changing the order the first char must be the last and the last char must be the first: \"hi how are you\";"'
        response: PromptResponse = PromptResponse(p, function_definitions, llm=llm) 
        response.generate_response() 
        print('======================================================================')
        print(response.response.content)
        break
    
    print("__main__")

def foo():
    from src.util.token_tree import TokenNode
    node = TokenNode()
    node.add_tokens([1,2,3])
    node.add_tokens([11,22,33])
    print_tree(node)


if __name__ == "__main__":
    foo()
    exit()
    __main__()
    print("THE END")