import pytest
from translator import evaluate_expression, transform_toml_to_custom

def test_evaluate_expression_simple():
    constants = {'a': 2, 'b': 3}
    assert evaluate_expression("a b +", constants) == 5
    assert evaluate_expression("a b -", constants) == -1
    assert evaluate_expression("10 abs", constants) == 10

def test_evaluate_expression_complex():
    constants = {'array': [3, 1, 4, 2]}
    assert evaluate_expression("array sort", constants) == [1, 2, 3, 4]

def test_invalid_expression():
    constants = {}
    with pytest.raises(ValueError):
        evaluate_expression("a b /", constants)