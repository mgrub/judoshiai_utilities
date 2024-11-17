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

parser.add_argument(
    "--port",
    default="8088",
    help="Port of JudoShiai webservice",
)

# parse CLI arguments
args = parser.parse_args()


def main(page: ft.Page):
    print("Initial route:", page.route)
    app = MatchApp(page, host=args.host, port=args.port)
    page.go(page.route)


ft.app(main)
