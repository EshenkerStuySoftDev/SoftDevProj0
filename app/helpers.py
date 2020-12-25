# We're using "%~" to represent apostrophes in strings b/c sql wasn't working
def clean_apostrophes(string):
    output = ""
    for char in string:
        if char == "'":
            output += '%~'
        else:
            output += char
    return output