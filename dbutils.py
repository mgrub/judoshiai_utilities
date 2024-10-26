import sqlite3 as sql


# alternative option:
# http://localhost:8088/sqlcmd?sql=SELECT%20%22index%22,%20category,%20numcomp,%20pos1,%20pos2,%20pos3,%20pos4%20FROM%20%22main%22.%22categories%22;
# http://localhost:8088/sqlcmd?sql=UPDATE%20%22main%22.%22matches%22%20SET%20blue_points%20=%200,%20white_points%20=%207%20WHERE%20(%20category%20==%2010017%20AND%20number%20==%201);

class JudoShiaiConnector:

    def __init__(self, db_path = "/home/maxwell/Desktop/judoshiai_test/tournament.shi"):
        self.db_path = db_path

    def select_cmd(self, cmd):
        # generic command to retrieve data from DB
        con = sql.connect(self.db_path)
        cur = con.cursor()
        res = cur.execute(cmd)
        res_list = res.fetchall()      
        con.close()

        return res_list

    def update_cmd(self, cmd):
        # generic command to update values in DB
        con = sql.connect(self.db_path)
        cur = con.cursor()
        res = cur.execute(cmd)
        con.commit()
        con.close()

        return 0
    
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
        return self.select_cmd(cmd)

    def get_matches(self, category_id):
        cmd = f"""
        SELECT category, number, blue_points, white_points
        FROM "main"."matches" 
        WHERE category == {category_id} ;
        """
        return self.select_cmd(cmd)
    
    def set_match(self, category_id, match_id, blue=0, white=0):
        cmd = f"""
            UPDATE "main"."matches" 
            SET blue_points = {blue}, white_points = {white}
            WHERE ( category == {category_id} AND number == {match_id});
        """
        return self.update_cmd(cmd)




if __name__ == "__main__":

    jsc = JudoShiaiConnector(db_path="/home/maxwell/Desktop/judoshiai_test/tournament.shi")

    print(jsc.get_categories())

    print(jsc.get_matches(10017))

    #jsc.set_match(10017, 1, 10, 0)
    #jsc.set_match(10017, 2, 0, 10)
    #jsc.set_match(10017, 3, 10, 0)
    #jsc.set_match(10017, 4, 0, 10)
    #jsc.set_match(10017, 5, 10, 0)
    #jsc.set_match(10017, 6, 7, 0)
    #jsc.set_match(10017, 7, 0, 7)
    #jsc.set_match(10017, 8, 7, 0)
    #jsc.set_match(10017, 9, 10, 0)
    #jsc.set_match(10017, 10, 10, 0)