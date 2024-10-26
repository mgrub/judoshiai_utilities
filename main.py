import flet as ft
import flet_core as ftc

from base import MatchApp


def main(page: ft.Page):
    print("Initial route:", page.route)
    app = MatchApp(page)
    page.go(page.route)


ft.app(main)