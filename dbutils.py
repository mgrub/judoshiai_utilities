import sqlite3 as sql

con = sql.connect("/home/maxwell/Desktop/judoshiai_test/tournament.shi")

cur = con.cursor()

get_categories = """
SELECT "index", category, numcomp, pos1, pos2, pos3, pos4
FROM "main"."categories" 
WHERE deleted == 0 ;
"""

get_matches = """
SELECT category, number, blue_points, white_points
FROM "main"."matches" 
WHERE category == 10017 ;
"""

res = cur.execute(get_categories)
for item in res.fetchall():
    print(item)

res = cur.execute(get_matches)
for item in res.fetchall():
    print(item)


con.close()