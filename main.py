import flet as ft
import flet_core as ftc
import argparse
import os

from base import MatchApp


# setup CLI
# some defaults for argparse interface
cwd = os.getcwd()

# argparse options
parser = argparse.ArgumentParser(
    prog="ShiMatchFill",
    description="Edit match results in an existing JudoShiai-database",
)

parser.add_argument(
    "--host",
    default="localhost",
    help="IP/URL to JudoShiai-host",
)

# parse CLI arguments
args = parser.parse_args()


def main(page: ft.Page):
    print("Initial route:", page.route)
    app = MatchApp(page, host=args.host)
    page.go(page.route)


ft.app(main)
