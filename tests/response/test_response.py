import json

from src.response.response import ResponseBuilder


def _appended_indent(builder: ResponseBuilder) -> str:
    """Call addIndent and return only the text it appended."""
    before = len(builder.content)
    assert builder.addIndent() is builder
    return builder.content[before:]

class TestResponseBuilder():
    def test_empty(self) -> None:
        builder = ResponseBuilder()
        assert str(builder) == ""
        assert builder.indent == 0

    def test_empty_dict(self) -> None:
        builder = ResponseBuilder()
        builder.openWith('{')
        builder.closeWith('}')
        assert str(builder) == "{\n}"
        assert json.loads(str(builder)) == {}
        assert builder.indent == 0

    def test_empty_list(self) -> None:
        builder = ResponseBuilder()
        builder.openWith('[')
        builder.closeWith(']')
        assert str(builder) == "[\n]"
        assert json.loads(str(builder)) == []

    def test_initial_content(self) -> None:
        builder = ResponseBuilder("header\n")
        builder.openWith('{')
        builder.closeWith('}')
        assert str(builder) == "header\n{\n}"

    def test_dict_with_one_key(self) -> None:
        builder = ResponseBuilder()
        builder.openWith('{')
        builder.appendLine('"a": 1')
        builder.closeWith('}')
        assert str(builder) == '{\n "a": 1\n}'
        assert json.loads(str(builder)) == {"a": 1}

    def test_dict_with_several_keys(self) -> None:
        builder = ResponseBuilder()
        builder.openWith('{')
        builder.appendLine('"a": 1,')
        builder.appendLine('"b": "two"')
        builder.closeWith('}')
        assert str(builder) == '{\n "a": 1,\n "b": "two"\n}'
        assert json.loads(str(builder)) == {"a": 1, "b": "two"}

    def test_list_of_dicts(self) -> None:
        builder = ResponseBuilder()
        builder.openWith('[')
        builder.openWith('{')
        builder.appendLine('"prompt": "Greet shrek"')
        builder.closeWith('}')
        builder.closeWith(']')
        assert str(builder) == '[{\n  "prompt": "Greet shrek"\n }\n]'
        assert json.loads(str(builder)) == [{"prompt": "Greet shrek"}]
        assert builder.indent == 0

    def test_indent_grows_and_shrinks(self) -> None:
        builder = ResponseBuilder()
        assert _appended_indent(builder) == ""
        builder.openWith('{')
        assert _appended_indent(builder) == " "
        builder.openWith('{')
        assert _appended_indent(builder) == "  "
        builder.closeWith('}')
        assert _appended_indent(builder) == " "
        builder.closeWith('}')
        assert _appended_indent(builder) == ""

    def test_custom_indent_str(self) -> None:
        builder = ResponseBuilder(indent_str="    ")
        builder.openWith('{')
        builder.appendLine('"a": 1')
        builder.closeWith('}')
        assert str(builder) == '{\n    "a": 1\n}'

    def test_initial_indent(self) -> None:
        builder = ResponseBuilder(initial_indent=2)
        assert builder.addIndent() is builder
        assert str(builder) == "  "
        builder.appendLine('"a": 1')
        assert str(builder) == '  \n  "a": 1'

    def test_initial_indent_with_custom_indent_str(self) -> None:
        builder = ResponseBuilder(indent_str="\t", initial_indent=1)
        builder.openWith('{')
        builder.appendLine('"a": 1')
        builder.closeWith('}')
        assert str(builder) == '{\n\t\t"a": 1\n\t}'
        assert builder.indent == 1

    def test_append_line_without_open(self) -> None:
        builder = ResponseBuilder()
        builder.appendLine("x")
        assert str(builder) == "\nx"
