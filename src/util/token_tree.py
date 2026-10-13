from src.parsing.functions_definitions import FunctionDefinition

class TokenNode():
    def __init__(self, token: int | None = None):
        self.token: int | None = token
        self.children: dict[int, TokenNode] = {}
        self.isentry: bool = False

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
            node = node.get_child(token)
            if node is None:
                return False
        return node.isentry