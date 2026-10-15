from src.parsing.prompts_file import Prompt
from src.parsing.functions_definitions import FunctionDefinition
from src.util.token_tree import TokenNode
from typing import TYPE_CHECKING
from math import inf
from abc import ABC, abstractmethod
import json

from llm_sdk import Small_LLM_Model

class ResponseBuilder():
    def __init__(self, prompt: str = "", indent_str: str = " ", initial_indent: int = 0):
        self.content: str = prompt
        self.indent_str = indent_str
        self.indent = initial_indent

    def addIndent(self) -> "ResponseBuilder":
        self.append(self.indent_str * self.indent)
        return self
        return self.indent_str * self.indent

    def openWith(self, c: str) -> "ResponseBuilder":
        self.indent += 1
        self.content += c
        return self

    def closeWith(self, c: str) -> "ResponseBuilder":
        self.indent -= 1
        self.appendLine(c)
        return self

    def appendLine(self, string: str) -> "ResponseBuilder":
        # self.content += '\n' + self.addIndent() + string
        return self.append('\n').addIndent().append(string)

    def append(self, string: str) -> "ResponseBuilder":
        self.content += string
        return self

    def __str__(self) -> str:
        return self.content

# class LogitPicker(ABC):
#     @abstractmethod
#     def __init__(self, llm: Small_LLM_Model):
#         ...

#     @abstractmethod
#     def pick_logit(logits: list[int]):
#         ...

# class MultiOptionPicker(ABC):
#     def __init__(self,
#         llm: Small_LLM_Model,
#         functions_list: list[FunctionDefinition]
#     ):
#         self.func_token_tree: TokenNode = TokenNode()
#         for fun_def in self.functions_definitions:
#             tokens = self.llm.encode(fun_def.name)[0].tolist()
#             self.func_token_tree.add_tokens(tokens)
        


class PromptResponse():
    def __init__(
        self,
        prompt: Prompt,
        function_definitions: list[FunctionDefinition],
        llm: Small_LLM_Model | None = None
    ):
        self.functions_definitions: list[FunctionDefinition] = function_definitions
        self.llm = llm if llm else Small_LLM_Model(cache_dir="./models", local_files_only=True)              # I is using the local option llm model
        self.prompt = prompt
        instruction: str = self.generate_init_instruction(prompt)
        self.response: ResponseBuilder = ResponseBuilder(instruction)

    def generate_init_instruction(self, prompt:Prompt) -> str:
        instruction: str = 'You will be given a list of functions in json format.\n'
        instruction += 'Then you will be given a task and must decide which of the fuctions fits this purpose\n'
        instruction += 'You must generate a json with the original prompt the name of the function for doing the task and the argument values\n'
        instruction += '\n'
        instruction += 'FUNCTIONS LIST: \n'
        functions = [f.model_dump() for f in self.functions_definitions]
        instruction += json.dumps(functions) + '\n'
        instruction += '\n'
        instruction += 'TASK: \n'
        instruction += prompt.prompt + '\n'
        instruction += '\n'
        instruction += "JSON RESPONSE: \n"
        return instruction

    def generate_response(self) -> str:
        self.response.openWith('[')
        self.response.openWith('{')
        self.add_prompt()
        self.add_function()
        self.add_arguments()
        self.response.closeWith('}')
        self.response.closeWith(']')

        return str(self.response)

    #TODO delte
    def build_tokenized_functions_tree(self) -> TokenNode:
        tokenized_functions_tree: TokenNode = TokenNode()
        for fun_def in self.functions_definitions:
            tokens = self.llm.encode(fun_def.name)[0].tolist()
            tokenized_functions_tree.add_tokens(tokens)
        return tokenized_functions_tree

    def add_prompt(self) -> None:
        self.response.appendLine(f'"prompt": "{self.prompt.prompt}",')

    def add_function(self) -> str:
        current_token_node: TokenNode = self.build_tokenized_functions_tree()
        self.response.appendLine('"name": "')

        enc_prompt: list[int] = self.llm.encode(self.response.content).tolist()[0]
        enc_function: list[int] = []
        end_token_list: list[int] = self.llm.encode('"').tolist()[0]
        if len(end_token_list) !=1:
            raise ValueError('with the current tokenizer " is not encoded as a single token')
        else:
            end_token: int = end_token_list[0]
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
            if next_encoded == end_token:
                break
            enc_prompt.append(next_encoded)
            enc_function.append(next_encoded)
            # it will not get None because the tokens that are not childs got probability -inf
            current_token_node = current_token_node.get_child(next_encoded) # type: ignore[assignment] 
        dec_func: str = self.llm.decode(enc_function)
        self.response.append(dec_func + '",')
        return dec_func


    def add_arguments(self) -> None:
        ...

    def add_one_argument(self) -> None:
        ...

