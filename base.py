import asyncio

import flet as ft

from dbutils import JudoShiaiConnector_WEB


class MatchApp:
    def __init__(self, page: ft.Page, host="localhost"):

        # DB connector
        self.jsc = JudoShiaiConnector_WEB(host)

        # init
        self.page = page
        self.page.title = "JudoShiai Match Result GUI"

        # cache
        self.matches = {}
        self.competitors = {}

        # layout and style
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.char_box_size = 35

        # routing and navigation
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop

        # define reusable app bar
        self.appbar_items = [
            ft.PopupMenuItem(content="Main", on_click=self.open_home()),
            ft.PopupMenuItem(content="About", on_click=self.open_about()),
            ft.PopupMenuItem(content="Settings", on_click=self.open_settings()),
        ]

        self.appbar = ft.AppBar(
            leading=ft.Icon(ft.Icons.CLOUD),
            leading_width=100,
            title=ft.Text(self.page.title, size=20, text_align="start"),
            center_title=False,
            toolbar_height=75,
            bgcolor=ft.Colors.LIGHT_BLUE_ACCENT_700,
            actions=[
                ft.Container(
                    content=ft.PopupMenuButton(items=self.appbar_items),
                    margin=ft.margin.Margin().only(left=50, right=25),
                )
            ],
        )
        self.page.appbar = self.appbar
        self.page.update()

    async def route_change(self, e):
        troute = ft.TemplateRoute(self.page.route)

        self.page.views.clear()

        if troute.match("/"):
            await self.set_overview_view()

        elif troute.match("/category/:id"):
            qid = troute.id
            await self.set_category_view(qid)

        elif troute.match("/about"):
            self.set_about_view()

        elif troute.match("/settings"):
            self.set_settings_view()

        else:
            print("Unknown Path: ", e.route)

        self.page.update()

    async def set_overview_view(self):
        self.solution_found = []

        categories = await self.jsc.get_categories()

        columns = []

        for cat in categories:
            is_finished = self.check_status(cat)
            color = ft.Colors.LIGHT_BLUE_100 if is_finished else ft.Colors.WHITE
            item = ft.Container(
                content=ft.Text(cat[1], size=30),
                col={"sm": 6, "md": 4, "xl": 2},
                on_click=self.open_category(cat[0]),
                margin=10,
                padding=10,
                alignment=ft.alignment.Alignment.CENTER,
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
            controls=view_elements,
            route="/",
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        )
        self.page.views.append(view)

    def check_status(self, cat):
        numcomp = int(cat[2])
        pos = cat[3 : 3 + numcomp]

        if numcomp > 0:
            is_finished = False if 0 in pos else True
        else:
            is_finished = False

        return is_finished

    async def set_category_view(self, cid):

        matches = await self.jsc.get_matches(cid)
        cat_info = await self.jsc.get_category_info(cid)
        rows = []

        for match in matches:
            mi = await self.match_item(match)
            rows.append(mi)

        back_button = ft.Button(
            content="Back",
            icon=ft.Icons.ARROW_BACK,
            on_click=self.open_home(),
            elevation=1,
        )

        reset_matches_button = ft.Button(
            content="CLEAR ALL MATCHES",
            icon=ft.Icons.WARNING,
            on_click=self.reset_matches(matches),
            color=ft.Colors.RED,
            elevation=1,
        )

        view = ft.View(
            controls=[
                self.appbar,
                back_button,
                ft.Text(cat_info[0], size=40),
                *rows,
                ft.Row(
                    [back_button, reset_matches_button],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            route=f"/category/{cid}",
            scroll=ft.ScrollMode.AUTO,
        )
        self.page.views.append(view)

    def set_about_view(self):
        view = ft.View(
            controls=[
                self.appbar,
                ft.Text(
                    size=30,
                    spans=[
                        ft.TextSpan("SV Luftfahrt Berlin e.V.\n"),
                        ft.TextSpan("Maximilian Gruber"),
                    ],
                ),
            ],
            route="/about",
        )
        self.page.views.append(view)

    def set_settings_view(self):
        button_reset = ft.Button(
            content="Reset user data",
            on_click=self.reset_cache,
            icon=ft.Icons.RESTART_ALT,
            elevation=1,
        )
        view_elements = [self.appbar, button_reset]
        view = ft.View(controls=view_elements, route="/settings")
        self.page.views.append(view)

    def reset_matches(self, matches):

        def reset_cat_matches(e):
            for m in matches:
                category_id = m[0]
                match_id = m[1]
                self.reset_points(category_id, match_id)

        return reset_cat_matches

    async def view_pop(self, e):
        print("View pop:", e.view)
        self.page.views.pop()
        top_view = self.page.views[-1]
        await self.page.push_route(top_view.route)

    def open_category(self, cid):
        open_cid = lambda e: asyncio.create_task(
            self.page.push_route(f"/category/{cid}")
        )
        return open_cid

    def open_home(self):
        call = lambda e: asyncio.create_task(self.page.push_route("/"))
        return call

    def open_about(self):
        call = lambda e: asyncio.create_task(self.page.push_route("/about"))
        return call

    def open_settings(self):
        call = lambda e: asyncio.create_task(self.page.push_route("/settings"))
        return call

    def row_container_hover(self, e):
        e.control.bgcolor = ft.Colors.LIGHT_BLUE_50 if e.data == "true" else ""
        e.control.update()

    async def refresh_match_item(self, match):
        cat_id = match[0]
        match_number = match[1]

        # retrieve match informations
        match_info = await self.jsc.get_match_info(cat_id, match_number)
        if cat_id in self.matches.keys():
            self.matches[cat_id][match_number] = match_info
        else:
            self.matches[cat_id] = {match_number: match_info}

        # update info about competitor blue
        blue_info = await self.jsc.get_competitor_info(match_info[0])
        self.competitors[match_info[0]] = blue_info

        # update info about competitor white
        white_info = await self.jsc.get_competitor_info(match_info[1])
        self.competitors[match_info[1]] = white_info

        return match_info, blue_info, white_info

    async def match_item(self, match):

        cat_id = match[0]
        match_number = match[1]

        if (
            cat_id in self.matches.keys()
            and match_number in self.matches[cat_id].keys()
        ):
            match_info = self.matches[cat_id][match_number]
            blue_info = self.competitors[match_info[0]]
            white_info = self.competitors[match_info[1]]
        else:
            match_info, blue_info, white_info = await self.refresh_match_item(match)

        async def refresh_callback(e):
            # this is a bit quick'n'dirty, but at least it works :-)
            match_info, blue_info, white_info = await self.refresh_match_item(match)

            blue_box.content.controls[0].value = f"{blue_info[1]} {blue_info[0]}"
            blue_box.content.controls[1].value = f"({blue_info[2]})"

            white_box.content.controls[0].value = f"{white_info[1]} {white_info[0]}"
            white_box.content.controls[1].value = f"({white_info[2]})"

            self.page.update()

        refresh_button = ft.IconButton(icon=ft.Icons.REFRESH, on_click=refresh_callback)
        blue_box = self.competitor_box(blue_info, color=ft.Colors.WHITE)
        blue_points = self.match_result_radiogroup(
            cat_id, match_number, match_info, is_blue=True
        )

        white_box = self.competitor_box(white_info, color=ft.Colors.BLUE_300)
        white_points = self.match_result_radiogroup(
            cat_id, match_number, match_info, is_blue=False
        )

        opacity = 1.0
        if blue_info[0] == "empty" or white_info[0] == "empty":
            opacity = 0.3

        content = [
            ft.Container(
                content=ft.Column([ft.Text(match[1], size=22), refresh_button]),
                col={"sm": 12, "md": 1, "xxl": 0.5},
                opacity=opacity,
            ),
            ft.Container(
                content=ft.Row([blue_box, blue_points]),
                col={"sm": 12, "md": 10, "xxl": 5},
                opacity=opacity,
            ),
            ft.Container(
                content=ft.Row([white_box, white_points]),
                col={"sm": 12, "md": 10, "xxl": 5},
                opacity=opacity,
            ),
            ft.Divider(),
        ]

        item = ft.ResponsiveRow(controls=content, alignment=ft.MainAxisAlignment.END)

        return item

    def competitor_box(self, info, color=ft.Colors.BLUE_300):
        # if you change something here, please also check `refresh_callback`

        name = f"{info[1]} {info[0]}"
        club = f"({info[2]})"

        box = ft.Container(
            content=ft.Column([ft.Text(name, size=30), ft.Text(club, size=22)]),
            border=ft.border.Border().all(1, ft.Colors.GREY_300),
            margin=10,
            padding=10,
            alignment=ft.alignment.Alignment.CENTER_LEFT,
            bgcolor=color,
            height=100,
            border_radius=10,
            expand=3,
        )

        return box

    def match_result_radiogroup(self, cat_id, match_number, match_info, is_blue=True):

        if is_blue:
            init_value = self.convert_and_simplify_score(match_info[2])
        else:
            init_value = self.convert_and_simplify_score(match_info[3])

        on_change = self.update_points(cat_id, match_number, is_blue)

        radio_group = ft.RadioGroup(
            ft.Row(
                [
                    ft.Column(
                        [ft.Text("0"), ft.Radio(value=0x00000, label="")],
                        alignment=ft.alignment.Alignment.CENTER,
                    ),
                    ft.Column(
                        [ft.Text("1"), ft.Radio(value=0x00010, label="")],
                        alignment=ft.alignment.Alignment.CENTER,
                    ),
                    ft.Column(
                        [ft.Text("5"), ft.Radio(value=0x00100, label="")],
                        alignment=ft.alignment.Alignment.CENTER,
                    ),
                    ft.Column(
                        [ft.Text("7"), ft.Radio(value=0x01000, label="")],
                        alignment=ft.alignment.Alignment.CENTER,
                    ),
                    ft.Column(
                        [ft.Text("10"), ft.Radio(value=0x10000, label="")],
                        alignment=ft.alignment.Alignment.CENTER,
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

    def convert_and_simplify_score(self, score_raw):
        score = int(score_raw)
        if score == 10:
            return 0x10000
        elif score == 7:
            return 0x01000
        elif score == 1:
            return 0x00010
        else:
            return 0x00000

    def update_points(self, category_id, match_id, is_blue):
        def update_db_points(e):
            winner_score = e.control.value
            if is_blue:
                self.jsc.set_match_result(
                    category_id, match_id, blue_score=winner_score, white_score=0x0
                )
            else:
                self.jsc.set_match_result(
                    category_id, match_id, blue_score=0x0, white_score=winner_score
                )
            # e.page.update()

        return update_db_points

    def reset_points(self, category_id, match_id):
        self.jsc.set_match_result(
            category_id, match_id, blue_score=0x0, white_score=0x0
        )

    def reset_cache(self, e):
        self.matches = {}
        self.competitors = {}
