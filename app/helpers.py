# Third Huge Freckled Elephant
# Ethan Shenker, Constance Chen, Andrew Jiang, Saqif Abedin
# P0 - To Be Named
# 2020-12-xx

import sqlite3


def a_clean(string: str) -> str:
    output = ""
    for char in string:
        if char == "'":
            output += "'"
        output += char
    return output


def tup_clean(arr: list) -> list:
    return [item[0] for item in arr]


def check_blog_conflicts(user_id: str, blog_name: str) -> bool:
    db = sqlite3.connect("blog.db")
    c = db.cursor()

    query = f"SELECT * FROM blogs WHERE user_id='{user_id}' AND blog_name='{blog_name}'"

    c.execute(query)
    conflicts = len(list(c))
    db.close()

    return conflicts > 0


def check_uuid_conflicts(user_id: str, blog_id: str) -> bool:
    pass
