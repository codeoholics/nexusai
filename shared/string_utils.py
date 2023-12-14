import re


def case_insensitive_replace(source_str, old_str, new_str):
    """Replace old_str with new_str in source_str in a case-insensitive manner."""
    # Using the re.IGNORECASE flag for case-insensitive search & replace
    return re.sub(re.escape(old_str), new_str, source_str, flags=re.IGNORECASE)

def extract_field_names_within_curly_braces(input_str):
    pattern = re.compile(r'\{(.*?)\}')

    # Find all non-overlapping matches in the input string
    # The function findall returns a list of all matched substrings
    field_names = pattern.findall(input_str)

    return field_names