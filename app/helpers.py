# Third Huge Freckled Elephant
# Ethan Shenker, Constance Chen, Andrew Jiang, Saqif Abedin
# P0 - To Be Named
# 2020-12-xx

def a_clean(string):
    output = ""
    for char in string:
        if char == "'":
            output += "'"
        output += char
    return output

def tup_clean(arr):
    return [item[0] for item in arr]