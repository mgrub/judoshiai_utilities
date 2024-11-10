import flet as ft
import flet_core as ftc
import argparse
import os

from base import MatchApp


# setup CLI
# some defaults for argparse interface
cwd = os.getcwd()
default_db = os.path.join(cwd, "competition.shi")

# argparse options
parser = argparse.ArgumentParser(
    prog="ShiMatchFill",
    description="Edit match results in an existing JudoShiai-database",
)

parser.add_argument(
    "-f",
    "--file",
    default=default_db,
    help="shi-file to use",
)

# parse CLI arguments
args = parser.parse_args()

def main(page: ft.Page):
    print("Initial route:", page.route)
    app = MatchApp(page, db_path=args.file)
    page.go(page.route)


ft.app(main)