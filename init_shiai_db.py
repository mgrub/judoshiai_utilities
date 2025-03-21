import shutil
import os
import copy
import shlex
import subprocess
import json
import pandas
from dbutils import JudoShiaiConnector_SQLITE
import argparse

# setup CLI
# some defaults for argparse interface
cwd = os.getcwd()
default_template = os.path.join(cwd, "template.shi")
default_ticket = os.path.join(cwd, "weight_ticket.svg")
default_competitors = os.path.join(cwd, "competitors.xlsx")

# argparse options
parser = argparse.ArgumentParser(
    prog="ShiPrep",
    description="Init Shiai-Template with Categories and Competitors",
)

parser.add_argument(
    "-t",
    "--template",
    default=default_template,
    help="shi-file to use as template DB",
)
parser.add_argument(
    "-c",
    "--competitors",
    default=default_competitors,
    help="xlsx-file with competitors",
)
parser.add_argument(
    "-o",
    "--output-dir",
    default=cwd,
    help="output directory to save prepared shi-DB",
)
parser.add_argument(
    "-n",
    "--name",
    default="competition",
    help="competition name (used for file naming)",
)
parser.add_argument(
    "--ignore-weight-cat",
    action='store_true',
    help="put all competitors into <agecat ?>",
)
parser.add_argument(
    "--use-youth-categories",
    action='store_true',
    help="use categories of style <u12m>",
)
parser.add_argument(
    "--create-tickets",
    action='store_true',
    help="create PDF weight tickets",
)
parser.add_argument(
    "--ticket-template",
    default=default_ticket,
    help="svg-file to use as template for weight tickets",
)
parser.add_argument(
    "--ticket-debug-mode",
    action='store_true',
    help="suppress actual pdf creation",
)

# parse CLI arguments
args = parser.parse_args()
template = args.template
output_directory = args.output_dir
competitors_xlsx = args.competitors
competitors_json = os.path.join(output_directory, f"competitors_{args.name}.json")
shi_path = os.path.join(output_directory, f"{args.name}.shi")

# stop if file already existing
if os.path.exists(shi_path):
    print(
        f"\nTarget path <{shi_path}> already exists.\nPlease rename or delete to proceed.\n"
    )
    exit()

# copy template
shutil.copy(template, shi_path)

# connect to shi file
db = JudoShiaiConnector_SQLITE(db_path=shi_path)

# init categories
catdefs = db.get_category_definitions()
for i, catdef in enumerate(catdefs):
    ix = i + 10013
    cat_name = catdef[0] + catdef[1]

    db.insert_category(cat_name, ix)


# init competitors
def age_cat_from_age_and_gender(age_raw, gender_raw):
    age_cat = ""
    
    if args.use_youth_categories:
        age_cat += age_raw

        if gender_raw == "female":
            age_cat += "w"
        elif gender_raw == "male":
            age_cat += "m"

    else:
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

        if args.ignore_weight_cat:
            weight_cat = "?"
            weight = 1000
        else:
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
            "ix": i + 10,
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

# create tickets
if args.create_tickets:
    debug_mode = args.ticket_debug_mode

    # read inkscape template
    template = open(args.ticket_template, "r").read()

    # make temporary folder
    tmp_folder = os.path.join(cwd, "tmp")
    if not os.path.exists(tmp_folder):
        os.mkdir(tmp_folder)

    # group by age and gender
    groups = df.groupby(["Gender"]) # ["AgeCat", "Gender"]

    for name, df_group in groups:

        # sort
        df_group = df_group.sort_values(["Club", "Name"]).fillna("")  # ["Weight", "Club", "Name"]

        # keep track of produced temporary files
        pdf_paths = []
        svg_paths = []
        inkscape_processes = []

        print("Group: ", name)

        # individuals
        for i, row in df_group.iterrows():
            
            # build age category
            age_raw = row["AgeCat"]
            gender_raw = row["Gender"]
            age_cat = age_cat_from_age_and_gender(age_raw, gender_raw)

            # print info
            print("{NAME}, {FNAME} ({CLUB}), {CAT}".format(
                NAME=row['Name'], 
                FNAME=row["FirstName"], 
                CLUB=row["Club"], 
                CAT=age_cat))

            # prepare all necessary entries
            replacements = {'__Name__': row['Name'],
                            '__FirstName__': row['FirstName'],
                            '__Club__': row['Club'],
                            '__AgeCat__': age_cat,
                            '__Nation__': row['Nation'],
                            '__WeightCat__': row['WeightCat'],
                            '__Weight__': row['Weight'] }

            # substitue in inkscape template
            tmp = copy.copy(template)
            for placeholder, replacement in replacements.items():
                tmp = tmp.replace(placeholder, replacement)
            
            # define output paths
            svg_path = os.path.join(tmp_folder, "{ID:04d}.svg".format(ID=row["#"]))
            pdf_path = os.path.join(tmp_folder, "{ID:04d}.pdf".format(ID=row["#"]))
            svg_paths.append(svg_path)
            pdf_paths.append(pdf_path)

            # write svg
            svg_file = open(svg_path, "w")
            svg_file.write(tmp)
            svg_file.close()

            # convert inkscape to pdf
            cmd_args = shlex.split("inkscape \"{SVG}\" --export-area-page --export-filename=\"{PDF}\"".format(SVG=svg_path, PDF=pdf_path))
            if not debug_mode:
                p = subprocess.Popen(cmd_args)
                inkscape_processes.append(p)

        # all processes were started in parallel, wait until all have finished before continuing 
        exit_codes = [p.wait() for p in inkscape_processes]

        # combine all pdf into single pdf for agecat
        input_paths = ' '.join(pdf_paths)
        output_path = os.path.join(cwd, '{NAME}_{CAT}.pdf'.format(NAME=args.name, CAT=name[0]))
        s = "gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile={OUT} {IN}".format(OUT=output_path, IN=input_paths)
        cmd_args = shlex.split(s)

        if not debug_mode:
            p = subprocess.Popen(cmd_args)
            p.communicate()

        # delete artifacts
        for path in svg_paths + pdf_paths:
            if os.path.exists(path):
                os.remove(path)
                