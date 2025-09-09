import re

def parse_variables_from_spel_expression(SpEL_expression):
    if not SpEL_expression:
        return []
    
    pattern = r"\$\{([a-zA-Z_][a-zA-Z0-9_]*)\}"
    return re.findall(pattern, SpEL_expression)