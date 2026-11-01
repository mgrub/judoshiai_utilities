import argparse
import os

import flet as ft
import flet_core as ftc

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


async def main(page: ft.Page):
    print("Initial route:", page.route)
    app = MatchApp(page, host=args.host)
    await app.route_change(page.route)


ft.run(main)
