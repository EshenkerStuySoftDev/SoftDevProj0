def clean_apostrophes(string):
    output = ""
    for char in string:
        if char == "'":
            output += '\\'
        output += char
    return output