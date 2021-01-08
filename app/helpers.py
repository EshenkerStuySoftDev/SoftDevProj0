# Third Huge Freckled Elephant
# Ethan Shenker, Constance Chen, Andrew Jiang, Saqif Abedin
# P0 - To Be Named
# 2020-12-xx

import sqlite3

# function to take care of issue in which sql queries
# aren't executed properly because of ' characters in them,
# so adds an extra ' to each ' that exists which acts as an
# escape char
def a_clean(string: str) -> str:
    output = ""
    for char in string:
        if char == "'":
            output += "'"
        output += char
    return output

# "cleans up" data structure returned from sql query
def tup_clean(arr: list) -> list:
    return [item[0] for item in arr]

# checks the db to ensure no blogs with the same name exist
def check_blog_conflicts(user_id: str, blog_name: str) -> bool:
    db = sqlite3.connect("blog.db")
    c = db.cursor()

    query = f"SELECT * FROM blogs WHERE user_id='{user_id}' AND blog_name='{blog_name}'"

    c.execute(query)
    conflicts = len(list(c))
    db.close()

    return conflicts > 0