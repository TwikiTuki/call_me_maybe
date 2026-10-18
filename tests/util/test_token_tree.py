from types import SimpleNamespace

from src.util.token_tree import TokenNode


class TestTokenNode():
    def test_init(self) -> None:
        root = TokenNode()
        assert root.token is None
        assert root.children == {}
        assert root.isentry is False

        node = TokenNode(7)
        assert node.token == 7
        assert node.children == {}
        assert node.isentry is False

    def test_add_non_existing_child(self) -> None:
        root = TokenNode()
        child = root.add_child(5)
        assert child.token == 5
        assert root.children == {5: child}
        assert child.isentry is False

    def test_add_existing_child(self) -> None:
        root = TokenNode()
        first = root.add_child(5)
        second = root.add_child(5)
        assert first is second
        assert len(root.children) == 1

    def test_get_child(self) -> None:
        root = TokenNode()
        child = root.add_child(5)
        assert root.get_child(5) is child

    def test_get_child_non_existing(self) -> None:
        root = TokenNode()
        root.add_child(5)
        assert root.get_child(6) is None

    def test_add_tokens_and_is_entry(self) -> None:
        # Adds a token list and confirms is_entry returns true when searching the list
        root = TokenNode()
        root.add_tokens([1, 2, 3])
        assert root.is_entry([1, 2, 3])
        root.add_tokens([1])
        assert root.is_entry([1])

    def test_add_tokens_and_not_is_entry(self) -> None:
        # Adds a token list and confirms is_entry returns false when searching another list
        root = TokenNode()
        root.add_tokens([1, 2, 3])
        assert not root.is_entry([4, 5, 6])
        assert not root.is_entry([1, 2])
        assert not root.is_entry([1, 2, 3, 4])
        assert not root.is_entry([])

    def test_add_tokens_diverging_from_start(self) -> None:
        # Adds two lists whose first tokens are already different
        root = TokenNode()
        root.add_tokens([1, 2, 3])
        root.add_tokens([4, 5, 6])
        assert set(root.children) == {1, 4}
        assert root.is_entry([1, 2, 3])
        assert root.is_entry([4, 5, 6])
        assert not root.is_entry([1, 5, 6])

    def test_add_tokens_diverging_after_shared_prefix(self) -> None:
        # Adds two lists whose first three tokens are the same and then are different
        root = TokenNode()
        assert root is not None
        root.add_tokens([1, 2, 3, 4])
        root.add_tokens([1, 2, 3, 5])
        assert set(root.children) == {1}
        node = root.get_child(1).get_child(2).get_child(3) # type: ignore[union-attr]
        assert node is not None
        assert set(node.children) == {4, 5}
        assert node.isentry is False
        assert root.is_entry([1, 2, 3, 4])
        assert root.is_entry([1, 2, 3, 5])
        assert not root.is_entry([1, 2, 3])

    def test_add_tokens_one_included(self) -> None:
        # Adds two lists of tokens, one is the same as the other but with extra tokens
        root = TokenNode()
        root.add_tokens([1, 2, 3, 4, 5])
        root.add_tokens([1, 2, 3])
        node = root.get_child(1).get_child(2).get_child(3) # type: ignore[union-attr]
        assert node.isentry is True
        assert set(node.children) == {4}
        assert root.is_entry([1, 2, 3])
        assert root.is_entry([1, 2, 3, 4, 5])
        assert not root.is_entry([1, 2, 3, 4])

    def test_get_all_children_id(self) -> None:
        root = TokenNode()
        assert root.get_all_children_id_list() == []

        # Adds children and checks they are returned as a list in insertion order
        root.add_child(3)
        root.add_child(1)
        root.add_child(2)
        assert isinstance(root.get_all_children_id_list(), list)
        assert root.get_all_children_id_list() == [3, 1, 2]

        # Adding an existing child must not duplicate its id
        root.add_child(1)
        assert root.get_all_children_id_list() == [3, 1, 2]

        # Adding grandchildren must not change the ids of the root
        root.add_tokens([1, 4, 5])
        assert root.get_all_children_id_list() == [3, 1, 2]
        child = root.get_child(1)
        assert child is not None
        assert child.get_all_children_id_list() == [4]
