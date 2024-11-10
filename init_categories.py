import shutil
import os
import json
import pandas
from dbutils import JudoShiaiConnector

template = "/home/maxwell/Desktop/judoshiai_test/masters_template.shi"
output_directory = "/home/maxwell/Desktop/judoshiai_test/MASTERS_2023_TEST"
competitors_xlsx = os.path.join(output_directory, "Meldungen_2023.xlsx")
competitors_json = os.path.splitext(competitors_xlsx)[0] + ".json"

# copy template
shi_path = os.path.join(output_directory, "competition.shi")
shutil.copy(template, shi_path)

# connect to shi file
db = JudoShiaiConnector(db_path=shi_path)

# init categories
catdefs = db.get_category_definitions()
for i, catdef in enumerate(catdefs):
    ix = i + 10013
    cat_name = catdef[0] + catdef[1]

    db.insert_category(cat_name, ix)


# init competitors
def age_cat_from_age_and_gender(age_raw, gender_raw):
    age_cat = ""
    if gender_raw == "female":
        age_cat += "Women"
    elif gender_raw == "male":
        age_cat += "Men"

    if age_raw == "open":
        pass
    elif age_raw == "u18":
        age_cat += " u18"
    elif age_raw[0] in ["ü", "Ü"]:
        age_cat += " +" + str(age_raw[1:])
    else:
        age_cat += " +" + str(age_raw)

    return age_cat


with open(competitors_xlsx, "rb") as f:
    df = pandas.read_excel(f, sheet_name="Meldungen mit DS", dtype={"WeightCat": str})

competitors = []

for i, row in df.iterrows():

    if pandas.notna(row["Name"]):

        age_cat = age_cat_from_age_and_gender(row["AgeCat"], row["Gender"])
        gender = 2 if row["Gender"] == "female" else 1

        weight_cat = ""
        weight = 0
        if pandas.notna(row["WeightCat"]):
            raw_weight_cat = row["WeightCat"]
            weight = int(raw_weight_cat) * 1000
            if raw_weight_cat[0] != "+":
                raw_weight_cat = "-" + raw_weight_cat
            weight_cat = raw_weight_cat + "kg"
        cat = f"{age_cat} {weight_cat}"

        birthyear = int(row["Born"]) if pandas.notna(row["Born"]) else 0
        country = row["Nation"] if pandas.notna(row["Nation"]) else ""

        competitor = {
            "ix": i+10,
            "last": row["Name"],
            "first": row["FirstName"],
            "club": row["Club"],
            "regcat": "",
            "category": cat,
            "country": country,
            "id": "",
            "comment": "",
            "coachid": "",
            "birthyear": birthyear,
            "belt": 0,
            "weight": weight,
            "flags": 0,
            "seeding": 0,
            "clubseeding": 0,
            "gender": gender,
        }

        competitor_db = {
            "index": competitor["ix"],
            "last": competitor["last"],
            "first": competitor["first"],
            "birthyear": competitor["birthyear"],
            "belt": competitor["belt"],
            "club": competitor["club"],
            "regcategory": competitor["regcat"],
            "weight": competitor["weight"],
            "visible": 1,
            "category": competitor["category"],
            "deleted": 0,
            "country": competitor["country"],
            "id": competitor["id"],
            "seeding": competitor["seeding"],
            "clubseeding": competitor["clubseeding"],
            "comment": competitor["comment"],
            "coachid": competitor["coachid"],
        }
        db.insert_competitor(**competitor_db)


        competitors.append(competitor)

with open(competitors_json, "w", encoding="utf8") as f:
    json.dump(competitors, f, indent=1, ensure_ascii=False)
