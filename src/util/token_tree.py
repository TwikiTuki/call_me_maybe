from src.parsing.functions_definitions import FunctionDefinition
from collections.abc import ValuesView

class TokenNode():
    def __init__(self, token: int | None = None):
        self.token: int | None = token
        self.children: dict[int, TokenNode] = {}
        self.isentry: bool = False

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"TokenNode({repr(self.token)})"

    def get_all_children(self) -> "ValuesView[TokenNode]":
        return self.children.values()

    def get_child(self, token: int) -> "TokenNode | None":
        return self.children.get(token)

    def add_child(self, token: int) -> "TokenNode":
        child: TokenNode | None = self.get_child(token)
        if child is None:
            child = TokenNode(token)
            self.children[token] = child
        return child

    def add_tokens(self, tokens: list[int]) -> None:
        node: TokenNode = self
        for token in tokens:
            node = node.add_child(token)
        node.isentry = True

    def is_entry(self, tokens: list[int]) -> bool:
        node: TokenNode | None = self
        for token in tokens:
            assert node is not None
            node = node.get_child(token)
            if node is None:
                return False
        assert node is not None
        return node.isentry

def print_tree(node: TokenNode, indent:int = 0, indent_str: str = " ") -> None:
    print(indent_str * indent + str(node))
    for n in node.get_all_children():
        print_tree(n, indent=indent+1, indent_str=indent_str)
