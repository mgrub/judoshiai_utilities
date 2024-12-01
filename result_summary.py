import argparse
import copy
import json
import re
import os


class ResultUtils:

    def __init__(self, results_dir):
        self.category_pattern = re.compile("^(.*?) ([\+\-\d]*)kg$")
        self.medal_points = {
            1: 10,
            2: 7,
            3: 5,
            4: 1,
            5: 1,
        }
        self.results_dir = results_dir

        results_path = os.path.join(results_dir, "results.json")
        with open(results_path, "r") as f:
            self.results = json.load(f)
        
        competitors_path = os.path.join(results_dir, "competitors.json")
        with open(competitors_path, "r") as f:
            self.competitors = json.load(f)

        self.parse_results()

    def parse_results(self):
        results_cleaned = []

        for cat in self.results:
            res = re.findall(self.category_pattern, cat["category"])
            if len(res) > 0:
                age_cat = res[0][0]
                weight_cat = res[0][1]
            else:
                age_cat = cat["category"]
                weight_cat = "0"

            clean_entry = {
                "age_cat": age_cat,
                "weight_cat": weight_cat,
                "numcomp": cat["numcomp"],
                "competitors": cat["competitors"],
            }
            results_cleaned.append(clean_entry)

        self.results_cleaned = sorted(
            results_cleaned, key=lambda x: (x["age_cat"], abs(int(x["weight_cat"])))
        )

    def winners_by_category(self, filter=".*", pos_max=3):

        for cat in self.results_cleaned:

            if re.fullmatch(filter, cat["age_cat"]):
                print(cat["age_cat"], cat["weight_cat"])
                for w in cat["competitors"]:
                    if w["pos"] <= pos_max:
                        print(f"  {w['pos']}. {w['first']} {w['last']} ({w['club']})")
                print("")

    def group_summary(self, filter=""):

        pos_by_club = {}

        clubsizes = self.teamsize(filter)

        print(f"\nGroup score {filter}")
        # get medals of each club
        for cat in self.results_cleaned:
            if re.fullmatch(filter, cat["age_cat"]):
                for w in cat["competitors"]:
                    club = w["club"]
                    if club in pos_by_club.keys():
                        pos_by_club[club].append(w["pos"])
                    else:
                        pos_by_club[club] = [w["pos"]]

        # calculate rating
        points_by_club = []
        for club, club_pos in pos_by_club.items():
            if True:
                points = [self.pos_to_point(pos) for pos in club_pos]
                point_sum = sum(points)
                points_by_club.append((club, point_sum))
        points_by_club = sorted(points_by_club, key=lambda x: x[1], reverse=True)
        

        # print results
        winners = {}
        if len(points_by_club) > 0:
            prev_points = points_by_club[0][1]
            place = 1
            for i, (club, points) in enumerate(points_by_club):

                if clubsizes[club] >= 3:
                    # same points should result in same place, but (e.g.) skip 4th place if we have 2x bronze
                    if points != prev_points:
                        place = place+1  # TODO: not correct, but works for now
                    
                    print(f"  {place}. {club} ({points} points) (Teamsize: {clubsizes[club]})")
                    prev_points = points

                    if place <= 3:
                        if place in winners.keys():
                            winners[place].append((club, points))
                        else:
                            winners[place] = [(club, points)]
        else:
            print("  No points so far in this group.")
        
        return winners

    def teamsize(self, filter=""):
        
        raw_competitors = []
        raw_clubs = []

        for c in self.competitors:
            first = c["first"]
            last = c["last"]
            club = c["club"]
            category = c["category"]

            if re.fullmatch(filter, category):
                raw_competitors.append((first, last, club))
                raw_clubs.append(club)
        
        individual_competitors = list(set(raw_competitors))
        clubs = list(set(raw_clubs))

        clubsizes = {}
        for club in clubs:
            c_per_club = [c for c in individual_competitors if c[2] == club]
            clubsizes[club] = len(c_per_club)

        return clubsizes

    def generate_certificates(self, winners, template_path, cat_name):
        print(template_path)
        
        with open(template_path, "r") as f:
            template = f.read()
        
        for place, clubs_and_points in winners.items():

            for club, points in clubs_and_points:
                print(place, club, points)

                output_svg = copy.copy(template)

                output_svg = output_svg.replace("@@GENDER_CAT@@", cat_name)
                output_svg = output_svg.replace("@@CLUB@@", club)
                output_svg = output_svg.replace("@@PLACE@@", str(place))

                save_clubname = "".join(x for x in club if x.isalnum())
                
                output_path = os.path.join(os.getcwd(), "urkunde", f"urkunde_{cat_name}_place_{place}_{save_clubname}.svg")

                with open(output_path, "w") as f:
                    f.write(output_svg)

    def pos_to_point(self, pos):
        if pos in self.medal_points.keys():
            return self.medal_points[pos]
        else:
            return 0


if __name__ == "__main__":

    # argparse interface
    parser = argparse.ArgumentParser(
        prog="ShiResultSummary",
        description="Quick summary of an existing results.json",
    )

    parser.add_argument(
        "--results-directory",
        default="results",
        help="path to results folder",
    )

    parser.add_argument(
        "--no-cat-results",
        action='store_false',
        help="suppress individual results",
    )

    parser.add_argument(
        "--cat-pattern",
        default=".*",
        help="only print categories matching pattern",
    )

    parser.add_argument(
        "--group-results",
        action='store_true',
        help="calculate group scores",
    )

    parser.add_argument(
        "--group-cert-template",
        default="",
        help="create certificates based on template for places 1+2+3",
    )

    args = parser.parse_args()

    # summarize results
    ru = ResultUtils(args.results_directory)

    if args.no_cat_results:
        ru.winners_by_category(filter=args.cat_pattern, pos_max=4)
    
    if args.group_results:
        winners_men = ru.group_summary("Men.*")
        winners_women = ru.group_summary("Women.*")

        if args.group_cert_template != "":
            ru.generate_certificates(winners_men, args.group_cert_template, "Männer")
            ru.generate_certificates(winners_women, args.group_cert_template, "Frauen")




# # testing
# ru = ResultUtils(
#     "/home/maxwell/Desktop/judoshiai_test/MASTERS_2023_TEST/results/"
# )
# # ru.winners_by_category(pos_max=3)  # filter="Men|Women"
# winners_men = ru.group_summary("Men.*")
# ru.teamsize("Men.*")
# winners_women = ru.group_summary("Women.*")

# group_cert_template = "/home/maxwell/Desktop/Masters_2024/urkunde/urkunde_template.svg"

# ru.generate_certificates(winners_men, group_cert_template, "Männer")
# ru.generate_certificates(winners_women, group_cert_template, "Frauen")
