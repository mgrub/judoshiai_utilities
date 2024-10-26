import flet as ft
from dbutils import JudoShiaiConnector


class MatchApp:
    def __init__(self, page: ft.Page, config_file="./config.json"):

        # DB connector
        self.db = JudoShiaiConnector(
            db_path="/home/maxwell/Desktop/judoshiai_test/tournament.shi"
        )

        # init
        self.page = page
        self.page.title = "JudoShiai Match Result GUI"

        # layout and style
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.char_box_size = 35

        # routing and navigation
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop

        # define reusable app bar
        self.appbar_items = [
            ft.PopupMenuItem(text="Main", on_click=self.open_home),
            ft.PopupMenuItem(text="About", on_click=self.open_about),
            ft.PopupMenuItem(text="Settings", on_click=self.open_settings),
        ]

        self.appbar = ft.AppBar(
            leading=ft.Icon(ft.icons.CLOUD),
            leading_width=100,
            title=ft.Text(self.page.title, size=20, text_align="start"),
            center_title=False,
            toolbar_height=75,
            bgcolor=ft.colors.LIGHT_BLUE_ACCENT_700,
            actions=[
                ft.Container(
                    content=ft.PopupMenuButton(items=self.appbar_items),
                    margin=ft.margin.only(left=50, right=25),
                )
            ],
        )
        self.page.appbar = self.appbar
        self.page.update()

    def route_change(self, e):
        troute = ft.TemplateRoute(self.page.route)

        self.page.views.clear()

        if troute.match("/"):
            self.set_overview_view()

        elif troute.match("/category/:id"):
            qid = troute.id
            self.set_category_view(qid)

        elif troute.match("/about"):
            self.set_about_view()

        elif troute.match("/settings"):
            self.set_settings_view()

        else:
            print("Unknown Path: ", e.route)

        self.page.update()

    def set_overview_view(self):
        self.solution_found = []

        categories = self.db.get_categories()

        columns = []

        for cat in categories:
            is_finished = self.check_status(cat)
            color = ft.colors.LIGHT_GREEN_300 if is_finished else ft.colors.GREY_300
            item = ft.Container(
                content=ft.Text(cat[1], size=30),
                col={"sm": 6, "md": 4, "xl": 2},
                on_click=self.open_category(cat[0]),
                margin=10,
                padding=10,
                alignment=ft.alignment.center,
                bgcolor=color,
                width=200,
                height=80,
                border_radius=10,
            )

            columns.append(item)

        # create rows
        resprows = ft.ResponsiveRow(columns)

        view_elements = [self.appbar, resprows]

        view = ft.View(
            "/",
            view_elements,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        )
        self.page.views.append(view)

    def check_status(self, cat):
        numcomp = cat[2]
        pos = cat[3 : 3 + numcomp]

        is_finished = False if 0 in pos else True

        return is_finished

    def set_category_view(self, cid):

        matches = self.db.get_matches(cid)
        cat_info = self.db.get_category_info(cid)
        rows = []

        for match in matches:
            mi = self.match_item(match)
            rows.append(mi)

        back_button = ft.ElevatedButton(
            text="Back", icon=ft.icons.ARROW_BACK, on_click=self.open_home
        )

        view = ft.View(
            f"/category/{cid}",
            [
                self.appbar,
                back_button,
                ft.Text(cat_info[0], size=40),
                *rows,
                back_button,
            ],
            scroll=ft.ScrollMode.AUTO,
        )
        self.page.views.append(view)

    def match_item(self, match):
        cat_id = match[0]
        match_number = match[1]
        match_info = self.db.get_match_info(cat_id, match_number)

        blue_info = self.db.get_competitor_info(match_info[0])
        blue_box = self.competitor_box(blue_info, color=ft.colors.BLUE_300)

        white_info = self.db.get_competitor_info(match_info[1])
        white_box = self.competitor_box(white_info, color=ft.colors.WHITE)

        content = [
            ft.Text(match[1]),
            white_box,
            ft.Text("..."),
            blue_box,
        ]

        item = ft.Row(controls=content)

        return item

    def competitor_box(self, info, color=ft.colors.BLUE_300):
        if len(info):
            name = f"{info[0][1]} {info[0][0]}"
            club = f"({info[0][2]})"
        else:
            name = "-----"
            club = ""
        
        box = ft.Container(
                content=ft.Column([ft.Text(name, size=30), ft.Text(club, size=15)]),
                border=ft.border.all(1, ft.colors.GREY_300),
                margin=10,
                padding=10,
                alignment=ft.alignment.center_left,
                bgcolor=color,
                
                width=500,
                height=100,
                border_radius=10,
            )

        return box

    def set_about_view(self):
        view = ft.View(
            "/about",
            [
                self.appbar,
                ft.Text(
                    size=30,
                    spans=[
                        ft.TextSpan("SV Luftfahrt Berlin e.V.\n"),
                        ft.TextSpan("Maximilian Gruber"),
                    ],
                ),
            ],
        )
        self.page.views.append(view)

    def set_settings_view(self):
        button_reset = ft.ElevatedButton(
            text="Reset user data",
            # on_click=self.init_user_storage,
            icon=ft.icons.RESTART_ALT,
        )
        view_elements = [self.appbar, button_reset]
        view = ft.View("/settings", view_elements)
        self.page.views.append(view)

    def view_pop(self, e):
        print("View pop:", e.view)
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.page.go(top_view.route)

    def open_category(self, cid):
        def open_cid(e):
            self.page.go(f"/category/{cid}")

        return open_cid

    def open_home(self, e):
        self.page.go("/")

    def open_about(self, e):
        self.page.go("/about")

    def open_settings(self, e):
        self.page.go("/settings")

    def row_container_hover(self, e):
        e.control.bgcolor = ft.colors.LIGHT_BLUE_50 if e.data == "true" else ""
        e.control.update()
