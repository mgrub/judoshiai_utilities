import flet as ft
from dbutils import JudoShiaiConnector


class MatchApp:
    def __init__(self, page: ft.Page, db_path="competition.shi"):

        # DB connector
        self.db = JudoShiaiConnector(db_path)

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

        if numcomp > 0:
            is_finished = False if 0 in pos else True
        else:
            is_finished = False

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

    def match_item(self, match):
        cat_id = match[0]
        match_number = match[1]
        match_info = self.db.get_match_info(cat_id, match_number)

        blue_info = self.db.get_competitor_info(match_info[0])
        blue_box = self.competitor_box(blue_info, color=ft.colors.BLUE_300)
        blue_points = self.match_result_radiogroup(
            cat_id, match_number, match_info, is_blue=True
        )

        white_info = self.db.get_competitor_info(match_info[1])
        white_box = self.competitor_box(white_info, color=ft.colors.WHITE)
        white_points = self.match_result_radiogroup(
            cat_id, match_number, match_info, is_blue=False
        )

        opacity = 1.0
        if blue_info[0] == "empty" or white_info[0] == "empty":
            opacity = 0.3

        content = [
            ft.Container(
                content=ft.Text(match[1], size=22),
                col={"sm": 12, "md": 1, "xxl": 0.5},
                opacity=opacity,
            ),
            ft.Container(
                content=ft.Row([white_box, white_points]),
                col={"sm": 12, "md": 10, "xxl": 5},
                opacity=opacity,
            ),
            ft.Container(
                content=ft.Row([blue_box, blue_points]),
                col={"sm": 12, "md": 10, "xxl": 5},
                opacity=opacity,
            ),
            ft.Divider(),
        ]

        item = ft.ResponsiveRow(controls=content, alignment=ft.MainAxisAlignment.END)

        return item

    def competitor_box(self, info, color=ft.colors.BLUE_300):

        name = f"{info[1]} {info[0]}"
        club = f"({info[2]})"

        box = ft.Container(
            content=ft.Column([ft.Text(name, size=30), ft.Text(club, size=22)]),
            border=ft.border.all(1, ft.colors.GREY_300),
            margin=10,
            padding=10,
            alignment=ft.alignment.center_left,
            bgcolor=color,
            height=100,
            border_radius=10,
            expand=3,
        )

        return box

    def match_result_radiogroup(self, cat_id, match_number, match_info, is_blue=True):

        if is_blue:
            init_value = match_info[2]
        else:
            init_value = match_info[3]

        on_change = self.update_points(cat_id, match_number, is_blue)

        radio_group = ft.RadioGroup(
            ft.Row(
                [
                    ft.Column(
                        [ft.Text("0"), ft.Radio(value="0", label="")],
                        alignment=ft.alignment.center,
                    ),
                    ft.Column(
                        [ft.Text("1"), ft.Radio(value="1", label="")],
                        alignment=ft.alignment.center,
                    ),
                    ft.Column(
                        [ft.Text("7"), ft.Radio(value="7", label="")],
                        alignment=ft.alignment.center,
                    ),
                    ft.Column(
                        [ft.Text("10"), ft.Radio(value="10", label="")],
                        alignment=ft.alignment.center,
                    ),
                ]
            ),
            value=init_value,
            on_change=on_change,
        )

        radio_container = ft.Container(
            content=radio_group,
            expand=1,
        )
        return radio_container

    def update_points(self, category_id, match_id, is_blue):
        def update_db_points(e):
            winner_points = e.control.value
            if is_blue:
                self.db.set_match_blue(category_id, match_id, winner_points)
            else:
                self.db.set_match_white(category_id, match_id, winner_points)
            # e.page.update()

        return update_db_points
