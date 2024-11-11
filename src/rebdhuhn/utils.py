"""utility functions"""


def _split_string(input_string: str, max_length: int) -> list[str]:
    """
    Splits the input string into multiple parts, each with a maximum length of `max_length`.
    The split occurs at the last space before reaching the limit.

    :param input_string: The string to be split.
    :param max_length: The maximum length for each part (default is 80).
    :return: A list of strings, each of length up to `max_length`.
    """
    parts: list[str] = []

    while len(input_string) > max_length:
        # Find the last space before the max length
        split_index_line_break = input_string.rfind("\n", 0, int(1.5 * max_length))
        split_index_whitespace: int = input_string.rfind(" ", 0, max_length)
        split_index: int
        # If no space is found, split at the max length
        if split_index_line_break != -1:  # prefer this one
            split_index = split_index_line_break
        elif split_index_whitespace != -1:
            split_index = split_index_whitespace
        else:
            split_index = max_length
        # Extract the part and append to the list
        part: str = input_string[:split_index].rstrip()
        if split_index_line_break != -1:
            part = part.replace("\n", "")
        parts.append(part)

        # Update the input_string to the remaining part
        input_string = input_string[split_index:].lstrip()

    # Add the remaining string if any
    if input_string:
        parts.append(input_string)

    return parts


def add_line_breaks(text: str, max_line_length: int = 80, line_sep: str = "\n") -> str:
    """
    Adds line_sep lines breaks between words after max max_line_length characters.
    If there already is a line break within the next max_line_length/2 after the max_line_length, we prefer to use that
    one instead of adding a new one. This is because we cannot decide if an existing line break is just an artefact of
    the .docx files (e.g. word break because the width of a column is limited) or if it has a functional meaning.
    A line break with a meaning is e.g. "Cluster Ablehnung:\n ..." <- here the line break structures the text in a good
    way, whereas `...Bilanzierungs-\nverantwortung...` is just an artefact.
    """
    return line_sep.join(_split_string(text, max_line_length))
