import re
from typing import Set

def parse_variables_from_spel_expression(spel_expression: str, full_path: bool=False) -> Set[str]:
    """
    Parse variables from SpEL expressions.
    
    Args:
        spel_expression: The SpEL expression string to parse
        full_path: If True, returns full path (e.g., 'step_699_result_1.body.data')
                   If False, returns only base variable name (e.g., 'step_699_result_1')
    
    Returns:
        List of variable names or paths found in the expression
    """
    if not spel_expression:
        return set([])
    
    if full_path:
        # Pattern to capture full path including dots and property access
        pattern = r"\$\{([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\}"
    else:
        # Pattern to capture only the base variable name (before any dots)
        pattern = r"\$\{([a-zA-Z_][a-zA-Z0-9_]*)(?:\.[^\}]+)?\}"
    
    return set(re.findall(pattern, spel_expression))


if __name__ == "__main__":
    # Test cases
    spel_expression = r"${step_699_result_1.body} != null"
    print("Base variable only:", parse_variables_from_spel_expression(spel_expression, full_path=False))
    print("Full path:", parse_variables_from_spel_expression(spel_expression, full_path=True))

    # Additional test with .body.data
    spel_expression = r"${step_699_result_1.body.data} != null"
    print("\nWith .body.data:")
    print("Base variable only:", parse_variables_from_spel_expression(spel_expression, full_path=False))
    print("Full path:", parse_variables_from_spel_expression(spel_expression, full_path=True))