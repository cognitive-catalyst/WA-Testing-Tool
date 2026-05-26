import re
from typing import Tuple

def parse_long_id(long_id: str) -> Tuple[str, str]:
    # if full_intent_id == "fallback_connect_to_agent":
    #     return "fallback", "fallback_connect_to_agent"
    
    # Pattern to match: parent_id_short_id with optional duplicate suffix
    # The short_id is the last component after underscore that contains letters and ends with digits
    # Parent ID can have multiple underscores and may or may not end with digits
    # Examples: "step_118_result_1", "digression_failure_result_1", "action_123_intent_456-2"
    pattern = r"^(.+)_([A-Za-z]+_?\d+)(-\d+)?$"
    match = re.match(pattern, long_id)
    if match:
        parent_id = match.group(1)
        short_id = match.group(2)
        suffix = match.group(3) or ""
        return parent_id + suffix, short_id

    raise ValueError(f"Unable to parse long id from '{long_id}'")

def build_long_id(parent_id: str, short_id: str) -> str:
    """
    Combines parent_id and short_id to create a long_id.
    
    Examples:
        build_long_id("action_123", "intent_456") -> "action_123_intent_456"
        build_long_id("action_123-2", "intent_456") -> "action_123_intent_456-2"
        build_long_id("digression_failure", "result_1") -> "digression_failure_result_1"
        build_long_id("digression_failure-2", "result_1") -> "digression_failure_result_1-2"
    
    Args:
        parent_id: Parent ID, possibly with duplicate suffix (e.g., "action_123", "digression_failure", or "action_123-2")
        short_id: Short ID to append (e.g., "intent_456", "result_1")
    
    Returns:
        Combined long ID with duplicate suffix at the end if present
    """
    # Check if parent_id has a duplicate suffix (-N)
    match = re.match(r"^(.+?)(-\d+)$", parent_id)
    if match:
        base_parent_id = match.group(1)  # e.g., "action_123" or "digression_failure"
        suffix = match.group(2)  # e.g., "-2"
        return f"{base_parent_id}_{short_id}{suffix}"
    
    # No suffix: just concatenate with underscore
    return f"{parent_id}_{short_id}"

if __name__ == "__main__":
    parent_id = "step_118"
    short_id = "result_1"
    print(build_long_id(parent_id, short_id))
    long_id = "step_118_result_1"
    print(parse_long_id(long_id))

    parent_id = "digression_failure"
    short_id = "result_1"
    print(build_long_id(parent_id, short_id))
    long_id = "digression_failure_result_1"
    print(parse_long_id(long_id))