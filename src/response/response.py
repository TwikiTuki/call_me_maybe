from src.parsing.prompts_file import Prompt
from src.parsing.functions_definitions import FunctionDefinition
from src.util.token_tree import TokenNode
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llm_sdk import Small_LLM_Model

class ResponseBuilder():
    def __init__(self, initial: str = "", indent_str = " ", initial_indent = 0):
        self.content: str = initial
        self.indent_str = indent_str
        self.indent = initial_indent

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

class ChooseFunction():
    def __init__(self, prompt: Prompt, functions: list[FunctionDefinition], response: ResponseBuilder, llm: "Small_LLM_Model"):
        self.prompt = prompt
        self.llm = llm
        self.functions_tree: TokenNode = self.create_functions_tree(functions)
        self.response = response

    def create_functions_tree(self, functions: list[FunctionDefinition]) -> TokenNode:
        root: TokenNode = TokenNode()
        for function in functions:
            tokens: list[int] = self.llm.encode(function.name)[0].tolist()
            root.add_tokens(tokens)
        return root

class PromptResponse():
    def __init__(self, prompt: Prompt,  function_definitions: list[FunctionDefinition]):
        self.prompt: Prompt = prompt
        self.functions: list[FunctionDefinition] = function_definitions
        self.response: ResponseBuilder = ResponseBuilder(prompt + '\n')

    def generate_response(self) -> str:
        self.response.openWith('[')
        self.response.openWith('{')
        self.response.appendLine(f'"prompt": "{self.prompt}"')
        self.response.closeWith('}')
        self.response.closeWith(']')

        return str(self.response)