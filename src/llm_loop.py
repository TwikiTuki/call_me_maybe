print("hellow from src/__main__.py")

from llm_sdk import Small_LLM_Model


INPUT_STR = "-Hellow"

INPUT_STR = '''
[SUBJECT]
you are given one operation and must fill the kind of operation the operand1 the operand2 and the result in the following template
<start template>
operation=
operand1=
operand2=
result=
operation=
<end template>
The first number is operand1 and the second number is operand2. the operations may be + or -.
If the operation is + you must write addition if the operation is - you must write substraction.
You have a couple of examples to take as refrence. But on the exericie the operands will be larger.

[EXAMPLES]
example 1
3 + 2
operation=addition
operand1=3
operand2=2
result=5

example 2
9 + 5
operation=addition
operand1=9
operand2=5
result=14

example 3
9 - 4
operation=substraction
operand1=9
operand2=4
result=5

example 4
10 + 11
operation=addition
operand1=10
operand2=11
result=21

example 5
30 - 11
operation=substraction
operand1=30
operand2=11
result=19

[EXERCICE]
# 11111111113308039020 - 11111111113308039019
#  do this operation 30-24
 do this operation 11111111113308039020 - 11111111113308039019
operation='''


INPUT_STR = '''
You will be given a list of functions in json format.
Then you will be given a task and must decide which of the fuctions fits this purpose
You must generate a json with the original prompt the name of the function for doing the task and the argument values

FUNCTIONS LIST: 
[{"name": "fn_add_numbers", "description": "Add two numbers together and return their sum.", "parameters": {"a": {"type": "number"}, "b": {"type": "number"}}, "returns": {"type": "number"}}, {"name": "fn_greet", "description": "Generate a greeting message for a person by name.", "parameters": {"name": {"type": "string"}}, "returns": {"type": "string"}}, {"name": "fn_reverse_string", "description": "Reverse a string and return the reversed result.", "parameters": {"s": {"type": "string"}}, "returns": {"type": "string"}}, {"name": "fn_get_square_root", "description": "Calculate the square root of a number.", "parameters": {"a": {"type": "number"}}, "returns": {"type": "number"}}, {"name": "fn_substitute_string_with_regex", "description": "Replace all occurrences matching a regex pattern in a string.", "parameters": {"source_string": {"type": "string"}, "regex": {"type": "string"}, "replacement": {"type": "string"}}, "returns": {"type": "string"}}]

TASK: 
Replace all vowels in 'Programming is fun' with asterisks

JSON RESPONSE: 
[
 {
  "prompt": "Replace all vowels in 'Programming is fun' with asterisks",
  "name": "fn_substitute_string_with_regex",
  "parameters": {
   "source_string": "Programming is fun",
   "regex": "([aeiouAEIO
  }
 }

'''

INPUT_STR='''
You will be given a list of functions in json format.
Then you will be given a task and must decide which of the fuctions fits this purpose
You must generate a json with the original prompt the name of the function for doing the task and the argument values

FUNCTIONS LIST: 
[{"name": "fn_add_numbers", "description": "Add two numbers together and return their sum.", "parameters": {"a": {"type": "number"}, "b": {"type": "number"}}, "returns": {"type": "number"}}, {"name": "fn_greet", "description": "Generate a greeting message for a person by name.", "parameters": {"name": {"type": "string"}}, "returns": {"type": "string"}}, {"name": "fn_reverse_string", "description": "Reverse a string and return the reversed result.", "parameters": {"s": {"type": "string"}}, "returns": {"type": "string"}}, {"name": "fn_get_square_root", "description": "Calculate the square root of a number.", "parameters": {"a": {"type": "number"}}, "returns": {"type": "number"}}, {"name": "fn_substitute_string_with_regex", "description": "Replace all occurrences matching a regex pattern in a string.", "parameters": {"source_string": {"type": "string"}, "regex": {"type": "string"}, "replacement": {"type": "string"}}, "returns": {"type": "string"}}]

TASK: 
Replace all vowels in 'Programming is fun' with asterisks

" U

JSON RESPONSE: 
[
 {
  "prompt": "Replace all vowels in 'Programming is fun' with asterisks",
  "name": "fn_substitute_string_with_regex",
  "parameters": {
   "source_string": "Programming is fun",
   "regex": "([aeiouAEIO
'''


# Downloads the model on the first run and reuses ./models afterwards.
# llm = Small_LLM_Model(cache_dir="./models", local_files_only=False)

# Offline mode: use this line after the model has been downloaded.
llm = Small_LLM_Model(cache_dir="./models", local_files_only=True)
encoded = llm.encode(INPUT_STR)[0].tolist()


for i in range(50):
    # print("BREAKING")
    # break
    logits: list[float] = llm.get_logits_from_input_ids(encoded)
    next_encoded: int = max(range(len(logits)), key = lambda i: logits[i])
    encoded.append(next_encoded)
    next_decoded = llm.decode([next_encoded])
    print("iter: ", llm.decode(encoded), f'<{next_decoded}>', flush=True)
    print()

def __main__() -> None:
    print("__main__")

if __name__ == "__main__":
    __main__()