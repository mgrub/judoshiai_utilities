import argparse
import re
from dbutils import JudoShiaiConnector_WEB

class MedalNeedUtils:
    def __init__(self, category_filter, hostname):
        self.category_filter = category_filter
        self.jsc = JudoShiaiConnector_WEB(host=hostname)

    def load_categories(self):
        categories = self.jsc.get_categories()
        return categories

    def write_output(self, categories):

        f = open("medal_needs.md", "w", encoding="UTF-8")
        f.write("# Medaillenübersicht\n\n")
        
        for cat in categories:
            catname = cat[1]
            if re.match(self.category_filter, catname):
                numcomp = int(cat[2])
                
                medals = ""
                if numcomp == 1:
                    medals = "G      "
                elif numcomp == 2:
                    medals = "G S    "
                elif numcomp == 3:
                    medals = "G S B  "
                elif numcomp >= 4:
                    medals = "G S B B"
                
                if numcomp:
                    f.write(f"- **{cat[1]}** :  `{medals}`  ({numcomp} Personen)\n")
        
        f.close()

if __name__ == "__main__":
    # argparse interface
    parser = argparse.ArgumentParser(
        prog="ShiMedalNeedUtils",
        description="Print overview of medal need for each category.",
    )

    parser.add_argument(
        "--category_filter",
        default=".*",
        help="regex filter of categories to include (default .* )",
    )

    parser.add_argument(
        "--host",
        default="localhost",
        help="URL/IP for host that runs JudoShiai",
    )

    args = parser.parse_args()

    # analyse competitors
    mnu = MedalNeedUtils(args.category_filter, args.host)

    cats = mnu.load_categories()
    mnu.write_output(cats)