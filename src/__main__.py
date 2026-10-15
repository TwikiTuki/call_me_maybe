print("hellow from src/__main__.py")    # TODO delte
import traceback
from src.parsing.arguments import parse_arguments, ProgramArgv
from src.parsing.functions_definitions import get_functions_from_file, FunctionDefinition
from src.parsing.prompts_file import get_prompts_from_file, Prompt
from src.util.token_tree import TokenNode
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


class ResponseBuilder():
    def __init__(self, prompt: str = ""):
        self.content: str = prompt + '\n'
        self.indent_str = " "
        self.indent = 0

    def addIndent(self) -> str:
        return self.indent_str * self.indent
        return self

    def openWith(self, c: str) -> None:
        self.indent += 1
        self.content += c
        return self

    def closeWith(self, c: str) -> None:
        self.indent -= 1
        self.appendLine(c)
        return self

    def appendLine(self, string: str) -> None:
        self.content += '\n' + self.addIndent() + string
        return self

    def append(self, string: str):
        self.content += string
        return self

    def __str__(self) -> str:
        return self.content


class PromptResponse():
    def __init__(self, prompt: Prompt,  function_definitions: list[FunctionDefinition], llm = None):
        self.prompt: Prompt = prompt
        self.functions_definitions: list[FunctionDefinition] = function_definitions
        self.llm = llm if llm else Small_LLM_Model(cache_dir="./models", local_files_only=True)              # I is using the local option llm model
        self.response: ResponseBuilder = ResponseBuilder(prompt.prompt)

    def build_tokenized_functions_tree(self) -> None:
        tokenized_functions_tree: TokenNode = TokenNode()
        for fun_def in self.functions_definitions:
            tokens = self.llm.encode(fun_def.name)[0].tolist()
            tokenized_functions_tree.add_tokens(tokens)
        return tokenized_functions_tree

    def add_prompt(self) -> None:
        self.response.appendLine(f'"prompt": "{self.prompt.prompt}",')

    def add_function(self) -> None:
        current_token_node: TokenNode = self.build_tokenized_functions_tree()
        self.response.appendLine('"name": "')

        enc_prompt: list[int] = self.llm.encode(self.response.content).tolist()[0]
        enc_function: list[int] = []
        end_token: int = self.llm.encode('"').tolist()[0]
        if len(end_token) !=1:
            raise ValueError('" with the current tokenizer " is not encoded as a single token')
        else:
            end_token = end_token[0]
        while True:
            logits: list[float] = self.llm.get_logits_from_input_ids(enc_prompt)
            allowed_tokens: list[int] = [t for t in current_token_node.children.keys()]
            if current_token_node.isentry == True:
                allowed_tokens.append(end_token)
            if len(allowed_tokens) == 0:
                raise ValueError("There are no more options")
            next_encoded: int = max(
                range(len(logits)),
                key = lambda i: logits[i] if i in allowed_tokens else -inf
            )
            enc_prompt.append(next_encoded)
            enc_function.append(next_encoded)
            if next_encoded == end_token:
                break
            current_token_node = current_token_node.get_child(next_encoded)
        dec_func: str = self.llm.decode(enc_function)
        self.response.append(dec_func + ',')
        return dec_func


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