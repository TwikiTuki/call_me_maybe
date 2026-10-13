print("hellow from src/__main__.py")    # TODO delte
import traceback
from src.parsing.arguments import parse_arguments, ProgramArgv
from src.parsing.functions_definitions import get_functions_from_file, FunctionDefinition
from src.parsing.prompts_file import get_prompts_from_file, Prompt
from sys import argv


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


class ResponseBuilder():
    def __init__(self, prompt: str = ""):
        self.content: str = prompt + '\n'
        self.indent_str = " "
        self.indent = 0

    def addIndent(self) -> str:
        return self.indent_str * self.indent

    def openWith(self, c: str) -> None:
        self.indent += 1
        self.content += c

    def closeWith(self, c: str) -> None:
        self.indent -= 1
        self.appendLine(c)

    def appendLine(self, string: str) -> None:
        self.content += '\n' + self.addIndent() + string

    def __str__(self) -> str:
        return self.content


class PromptResponse():
    def __init__(self, prompt: Prompt,  function_definitions: list[FunctionDefinition]):
        self.prompt: Prompt = prompt
        self.functions_definitions: list[FunctionDefinition] = function_definitions
        self.tokenized_functions_tree: TokenNode = TokenNode()
        self.response: ResponseBuilder = ResponseBuilder(prompt)

    def build_tokenized_functions_tree(self) -> None:
        for function_definition in self.functions_definitions:
            self.tokenized_functions_tree.add_tokens(function_definition.tokens)

    def add_prompt(self) -> None:
        self.response.appendLine(f'"prompt": "{self.prompt}"')

    def add_function(self) -> None:
        ...

    def add_arguments(self) -> None:
        ...

    def add_one_argument(self) -> None:
        ...


    def generate_response(self) -> str:
        self.response.openWith('[')
        self.response.openWith('{')
        self.add_prompt()
        self.add_function()
        self.add_arguments()
        self.response.closeWith('}')
        self.response.closeWith(']')

        return str(self.response)


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
    print("__main__")

if __name__ == "__main__":
    __main__()
    print("THE END")