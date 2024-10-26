import flet as ft
import flet_core as ftc

from base import MatchApp


def main(page: ft.Page):
    print("Initial route:", page.route)
    app = MatchApp(page)
    page.go(page.route)


if __name__ == "__main__":
    ft.app(target=main, view=ftc.types.WebRenderer)
