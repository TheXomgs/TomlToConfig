import sys
import re
import toml
import json
from typing import Any, Union

IDENTIFIER_RE = re.compile(r"^[_a-zA-Z][_a-zA-Z0-9]*$")

def evaluate_expression(expression: str, constants: dict) -> Any:
    tokens = expression.split()
    stack = []

    for token in tokens:
        if re.match(r"^-?\d+$", token):
            stack.append(int(token))
        elif token in constants:
            stack.append(constants[token])
        elif token == '+':
            b = stack.pop()
            a = stack.pop()
            stack.append(a + b)
        elif token == '-':
            b = stack.pop()
            a = stack.pop()
            stack.append(a - b)
        elif token == 'abs':
            a = stack.pop()
            stack.append(abs(a))
        elif token == 'sort':
            a = stack.pop()
            if isinstance(a, list):
                stack.append(sorted(a))
            else:
                raise ValueError("sort() can only be applied to arrays")
        else:
            raise ValueError(f"Unknown token: {token}")

    if len(stack) != 1:
        raise ValueError("Invalid expression")

    return stack[0]

def transform_value(value: Any, constants: dict) -> Union[str, int, float, list, dict]:
    if isinstance(value, list):
        return [transform_value(v, constants) for v in value]
    elif isinstance(value, dict):
        return {k: transform_value(v, constants) for k, v in value.items()}
    elif isinstance(value, str) and value.startswith(".(") and value.endswith(")."):
        expression = value[2:-2].strip()
        return evaluate_expression(expression, constants)
    elif isinstance(value, (int, float)):
        return value
    else:
        raise ValueError(f"Unsupported value type: {type(value)}")

def transform_toml_to_custom(input_toml: str) -> str:
    parsed_toml = toml.loads(input_toml)
    output_lines = []
    constants = {}

    def serialize_value(value: Any) -> str:
        if isinstance(value, list):
            return "[ " + "; ".join(serialize_value(v) for v in value) + " ]"
        elif isinstance(value, dict):
            lines = ["begin"]
            for k, v in value.items():
                lines.append(f"  {k} := {serialize_value(v)};")
            lines.append("end")
            return "\n".join(lines)
        elif isinstance(value, (int, float)):
            return json.dumps(value)
        else:
            raise ValueError(f"Cannot serialize value: {value}")

    for key, value in parsed_toml.items():
        transformed_value = transform_value(value, constants)
        if isinstance(transformed_value, (int, float, list, dict)):
            constants[key] = transformed_value
        output_lines.append(f"def {key} = {serialize_value(transformed_value)};")

    return "\n".join(output_lines)

def main():
    try:
        input_toml = sys.stdin.read()
        output_custom = transform_toml_to_custom(input_toml)
        print(output_custom)
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
