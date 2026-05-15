@staticmethod
def _parse_add_or_subtract_date_obj(add_or_subtract_date_obj, add_or_subtract_field):
    if add_or_subtract_field != "add" and add_or_subtract_field != "subtract":
        raise ValueError(f"The argument `add_or_subtract_date_obj` must be one of 'add' or 'subtract', instead got '{add_or_subtract_field}'")

    plus_or_minus = "plus" if add_or_subtract_field == "addition" else "minus"

    LHS = add_or_subtract_date_obj[0]["system_variable"]        # This should always be ${current_date} or ${current_time} I believe
    LHS_SpEL_expression = f"${{{LHS}}}"

    duration_obj = add_or_subtract_date_obj[1]["duration"]
    RHS_SpEL_expression = ""

    if "seconds" in duration_obj:
        RHS_SpEL_expression = f".{plus_or_minus}Seconds({duration_obj['seconds']})"
    elif "minutes" in duration_obj:
        RHS_SpEL_expression = f".{plus_or_minus}Minutes({duration_obj['minutes']})"
    elif "hours" in duration_obj:
        RHS_SpEL_expression = f".{plus_or_minus}Hours({duration_obj['hours']})"
    elif "days" in duration_obj:
        RHS_SpEL_expression = f".{plus_or_minus}Days({duration_obj['days']})"
    elif "months" in duration_obj:
        RHS_SpEL_expression = f".{plus_or_minus}Months({duration_obj['months']})"
    elif "years" in duration_obj:
        RHS_SpEL_expression = f".{plus_or_minus}Years({duration_obj['years']})"
    else:
        raise ValueError("Unknown duration object:", duration_obj)

    return LHS, f"{LHS_SpEL_expression}{RHS_SpEL_expression}", None

"""
This is from my pervious iteration. I don't see these fields in my current implementation
Maybe it's depreciated or something. I'm not sure
"""