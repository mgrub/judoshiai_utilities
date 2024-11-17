import sqlite3 as sql
import requests
import json


# only use for offline use, recommended to use WEB-connector during runtime
class JudoShiaiConnector_SQLITE:

    def __init__(self, db_path="tournament.shi"):
        self.db_path = db_path

    def select_cmd(self, cmd):
        # generic command to retrieve data from DB
        con = sql.connect(self.db_path)
        cur = con.cursor()
        res = cur.execute(cmd)
        res_list = res.fetchall()
        con.close()

        return res_list

    def update_or_insert_cmd(self, cmd):
        # generic command to update values in DB
        con = sql.connect(self.db_path)
        cur = con.cursor()
        res = cur.execute(cmd)
        con.commit()
        con.close()

        return 0

    def get_category_definitions(self):
        cmd = """
        SELECT agetext, weighttext
        FROM "main"."catdef" ;
        """
        return self.select_cmd(cmd)

    def insert_category(self, cat_name, ix=0):
        cmd = f"""
            INSERT INTO "main"."categories" ("index", "category", "tatami", "deleted", "group", "system", "numcomp", "table", "wishsys", "pos1", "pos2", "pos3", "pos4", "pos5", "pos6", "pos7", "pos8", "color") 
            VALUES ('{ix}', '{cat_name}', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '');
        """
        return self.update_or_insert_cmd(cmd)

    def insert_competitor(
        self,
        index,
        last,
        first,
        birthyear,
        belt,
        club,
        regcategory,
        weight,
        visible,
        category,
        deleted,
        country,
        id,
        seeding,
        clubseeding,
        comment,
        coachid,
    ):

        cmd = f"""
            INSERT INTO "main"."competitors" ("index", "last", "first", "birthyear", "belt", "club", "regcategory", "weight", "visible", "category", "deleted", "country", "id", "seeding", "clubseeding", "comment", "coachid")
            VALUES ('{index}', '{last}', '{first}', '{birthyear}', '{belt}', '{club}', '{regcategory}', '{weight}', '{visible}', '{category}', '{deleted}', '{country}', '{id}', '{seeding}', '{clubseeding}', '{comment}', '{coachid}');
        """
        return self.update_or_insert_cmd(cmd)


# only useable when JudoShiai is running
class JudoShiaiConnector_WEB:

    def __init__(self, host="localhost", port=8088):
        self.host = host
        self.port = port

    def select_cmd(self, cmd):
        # curl -X POST -H 'Content-Type: application/json' -d '{"op": "sql", "pw": "PASSWD", "cmd":"SELECT agetext, weighttext FROM main.catdef"}' http://localhost:8088/json
        url = f"http://{self.host}:{self.port}/json"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        json_data = {"op": "sql", "pw": "PASSWD", "cmd": cmd}

        response = requests.post(url, headers=headers, json=json_data)
        response.encoding = "utf-8"

        res_list = []
        if response.status_code == 200:
            res_list = json.loads(response.text)[1:]

        return res_list

    def get_categories(self):
        cmd = """
        SELECT "index", category, numcomp, pos1, pos2, pos3, pos4
        FROM "main"."categories" 
        WHERE deleted == 0 ;
        """
        return self.select_cmd(cmd)

    def get_category_info(self, cid):
        cmd = f"""
        SELECT category, numcomp, pos1, pos2, pos3, pos4
        FROM "main"."categories"
        WHERE "index" == {cid} ;
        """
        return self.select_cmd(cmd)[0]

    def get_match_info(self, cid, mid):
        cmd = f"""
        SELECT blue, white, blue_points, white_points
        FROM "main"."matches"
        WHERE "category" == {cid} AND "number" == {mid} ;
        """
        return self.select_cmd(cmd)[0]

    def get_competitor_info(self, cid):
        cmd = f"""
        SELECT last, first, club, birthyear, country
        FROM "main"."competitors"
        WHERE "index" == {cid} ;
        """
        if cid == 0:
            return ["unknown", "", "", "", ""]
        elif cid == 1:
            return ["empty", "", "", "", ""]
        else:
            return self.select_cmd(cmd)[0]

    def get_matches(self, category_id):
        cmd = f"""
        SELECT category, number, blue_points, white_points
        FROM "main"."matches" 
        WHERE category == {category_id} ;
        """
        return self.select_cmd(cmd)

    def set_match_result(self, category_id, match_id, blue_score, white_score):
        cmd = f"""
            UPDATE "main"."matches" 
            SET blue_points = {blue}, white_points = {white}
            WHERE ( category == {category_id} AND number == {match_id});
        """
        return self.update_or_insert_cmd(cmd)

    def set_match_blue(self, category_id, match_id, blue=0):
        cmd = f"""
            UPDATE "main"."matches" 
            SET blue_points = {blue}
            WHERE ( category == {category_id} AND number == {match_id});
        """
        return self.update_or_insert_cmd(cmd)

    def set_match_white(self, category_id, match_id, white=0):
        cmd = f"""
            UPDATE "main"."matches" 
            SET white_points = {white}
            WHERE ( category == {category_id} AND number == {match_id});
        """
        return self.update_or_insert_cmd(cmd)


if __name__ == "__main__":

    jsc_offline = JudoShiaiConnector_SQLITE(
        db_path="/home/maxwell/Desktop/judoshiai_test/tournament.shi"
    )
    print(jsc_offline.get_category_definitions())

    jsc_online = JudoShiaiConnector_WEB()
    print(jsc_online.get_categories())
    print(jsc_online.get_matches(10014))
    print(jsc_online.get_competitor_info(29))
