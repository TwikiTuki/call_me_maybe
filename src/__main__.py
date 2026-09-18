print("hellow from src/__main__.py")    # TODO delte
import traceback
from src.parsing.arguments import parse_arguments
from sys import argv


def __main__() -> None:
    print("__main__")
    try:
        arguments = parse_arguments(argv)
    except Exception as e:
        print(" :::: Something whent wrong while parsing the input parameters ::::")
        traceback.print_exception(e)
        return
    print("arguments: ")
    print(arguments)




if __name__ == "__main__":
    __main__()
    print("THE END")