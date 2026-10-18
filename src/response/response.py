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

    def appendLine(self, string: str | None = None) -> "ResponseBuilder":
        # self.content += '\n' + self.addIndent() + string
        string = string or ""
        return self.append('\n').addIndent().append(string)

    def append(self, string: str) -> "ResponseBuilder":
        self.content += string
        return self

    def __str__(self) -> str:
        return self.content

class LogitPicker(ABC):
    def __init__(self, llm: Small_LLM_Model):
        self.llm = llm

    def _single_token(self, text: str) -> int:
        tokens: list[int] = self.llm.encode(text).tolist()[0]
        if len(tokens) != 1:
            raise ValueError(f'with the current tokenizer {text} is not encoded as a single token')
        return tokens[0]

    @abstractmethod
    def pick_logit(self, logits: list[float]) -> int | None:
        """Return the picked token, or None when generation must stop.
        Implementations update their internal state with the picked token."""
        ...

class MultiOptionPicker(LogitPicker):
    def __init__(self, llm: Small_LLM_Model, function_definitions: list[FunctionDefinition]):
        super().__init__(llm)
        self.token_node: TokenNode = self._build_token_tree(function_definitions)
        self.end_token: int = self._single_token('"')

    def _build_token_tree(self, function_definitions: list[FunctionDefinition]) -> TokenNode:
        token_tree: TokenNode = TokenNode()
        for fun_def in function_definitions:
            tokens: list[int] = self.llm.encode(fun_def.name)[0].tolist()
            token_tree.add_tokens(tokens)
        return token_tree

    def pick_logit(self, logits: list[float]) -> int | None:
        allowed_tokens: list[int] = self.token_node.get_all_children_id_list()
        if self.token_node.isentry:
            allowed_tokens.append(self.end_token)
        if len(allowed_tokens) == 0:
            raise ValueError("There are no more options")
        picked: int = max(allowed_tokens, key=lambda t: logits[t])
        if picked == self.end_token:
            return None
        # it will not get None because picked is one of the children
        self.token_node = self.token_node.get_child(picked) # type: ignore[assignment]
        return picked


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
        self.response.appendLine().openWith('{')
        self.add_prompt()
        self.add_function_name()
        self.add_arguments()
        self.response.closeWith('}')
        self.response.closeWith(']')

        return str(self.response)

    def add_prompt(self) -> None:
        self.response.appendLine(f'"prompt": "{self.prompt.prompt}",')

    def add_function_name(self) -> str:
        self.response.appendLine('"name": "')
        picker = MultiOptionPicker(self.llm, self.functions_definitions)
        name: str = self.infer_text(picker)
        self.response.append('",')
        return name

    def infer_text(self, picker: LogitPicker) -> str:
        enc_prompt: list[int] = self.llm.encode(self.response.content).tolist()[0]
        enc_generated: list[int] = []
        while True:
            logits: list[float] = self.llm.get_logits_from_input_ids(enc_prompt)
            next_encoded: int | None = picker.pick_logit(logits)
            if next_encoded is None:
                break
            enc_prompt.append(next_encoded)
            enc_generated.append(next_encoded)
        dec_text: str = self.llm.decode(enc_generated)
        self.response.append(dec_text)
        return dec_text


    def add_arguments(self) -> None:
        ...

    def add_one_argument(self) -> None:
        ...

