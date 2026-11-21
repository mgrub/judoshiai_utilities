import asyncio
import os
import pathlib
import subprocess
import sys
from typing import Any, Awaitable, Callable

import flet as ft

from dbutils import JudoShiaiConnector_WEB
from ui_utils.match_ui_element import Match


class MatchApp:
    def __init__(self, page: ft.Page, host="localhost"):

        # DB connector
        self.jsc = JudoShiaiConnector_WEB(host)

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
            ft.PopupMenuItem(content="Main", on_click=self.open_home()),
            ft.PopupMenuItem(content="Reports", on_click=self.open_reports()),
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

        elif troute.match("/reports"):
            self.set_reports_view()

        elif troute.match("/about"):
            self.set_about_view()

        elif troute.match("/settings"):
            self.set_settings_view()

        else:
            print("Unknown Path: ", e.route)

        self.page.update()

    async def set_overview_view(self):
        self.solution_found = []

        categories = await self.jsc.get_categories_extended_info()
        # category status is int with binary meaning:
        # bit with val 1: MATCH_EXISTS       -> TRUE <=> Es gibt ein Match von category.
        # bit with val 2: MATCH_MATCHED      -> True <=>
        # Es gibt ein Match m von category, für das gilt:
        #     (m.deleted & DELETED) == 0 &&                             <- DELETED = 0x01
        #     (m.blue_points != 0 || m.white_points != 0) &&
        #     m.blue >= COMPETITOR &&                                   <- COMPETITOR = 9
        #     m.white >= COMPETITOR
        # bit with val 4: MATCH_UNMATCHED    -> True <=>
        # Es gibt ein Match m von category, für das gilt:
        #     (m.deleted & DELETED) == 0 &&                             <- DELETED = 0x01
        #     m.blue >= COMPETITOR &&                                   <- COMPETITOR = 9
        #     m.white >= COMPETITOR &&
        #     m.blue_points == 0 &&
        #     m.white_points == 0 &&
        #     (avl_get_competitor_status(m.blue) & HANSOKUMAKE) == 0 && <- HANSOKUMAKE = 0x02
        #     (avl_get_competitor_status(m.white) & HANSOKUMAKE) == 0
        # bit with val 8: ?
        # bit with val 16: REAL_MATCH_EXISTS
        # bit with val 32: SYSTEM_DEFINED    -> True <=> category.system != 0
        #
        # category completed if SYSTEM_DEFINED AND NOT MATCH_UNMATCHED
        # category started if MATCH_MATCHED
        # category drawn if MATCH_EXISTS

        columns = {}

        for cat in categories:
            color = self.get_match_color(cat)
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

            abstract_cat = cat[1][:cat[1].rfind("-") if cat[1].rfind("-") != -1 else cat[1].rfind("+")]
            columns.setdefault(abstract_cat, []).append(item)

        # create rows
        resprows = []
        for abstract_cat, cols in columns.items():
            resprows.append(ft.Divider())
            row = ft.ResponsiveRow(cols)
            def construct_close_open(row):
                def close_open(e):
                    row.visible = not row.visible
                    self.page.update()
                return close_open
            button = ft.Button("hide/ show", on_click=construct_close_open(row))
            resprows.append(ft.Row([ft.Text(abstract_cat, size=30), button]))
            resprows.append(row)
        resprows.append(ft.Divider())

        async def reload(e):
            self.page.views.clear()
            await self.set_overview_view()

        refresh_button = ft.IconButton(icon=ft.Icons.REFRESH, on_click=reload)

        view_elements = [self.appbar, refresh_button, *resprows]

        view = ft.View(
            controls=view_elements,
            route="/",
            horizontal_alignment=ft.CrossAxisAlignment.START,
            scroll=ft.ScrollMode.AUTO,
        )
        self.page.views.append(view)

    def get_match_color(self, cat):
        print(f"{cat=}")
        if cat[4] != "0" and cat[5] == "0":  # system defined and not match unmatched
            return ft.Colors.GREEN
        if cat[3] != "0":  # match_matched
            return ft.Colors.ORANGE
        if cat[2] != "0":  # match_exists
            return ft.Colors.YELLOW
        return ft.Colors.GREY

    async def set_category_view(self, cid):
        cat_label = (await self.jsc.get_category_info(cid))[0]
        matches = await self.jsc.get_matches(cid)
        rows = await self.match_items(cid, matches)

        async def reload(e):
            # hard reload
            self.page.views.clear()
            await self.set_category_view(cid)

        refresh_button = ft.IconButton(icon=ft.Icons.REFRESH, on_click=reload)

        back_button = ft.Button(
            content="Back",
            icon=ft.Icons.ARROW_BACK,
            on_click=self.open_home(),
            elevation=1,
        )

        reset_matches_button = ft.Button(
            content="CLEAR ALL MATCHES",
            icon=ft.Icons.WARNING,
            on_click=self.reset_matches(cid, [match[0] for match in matches]),
            color=ft.Colors.RED,
            elevation=1,
        )

        view = ft.View(
            controls=[
                self.appbar,
                ft.Row([back_button, refresh_button]),
                ft.Text(cat_label, size=40),
                *rows,
                ft.Row(
                    [back_button, refresh_button, reset_matches_button],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            route=f"/category/{cid}",
            scroll=ft.ScrollMode.AUTO,
        )
        self.page.views.append(view)

    def set_reports_view(self):

        buttons = []
        shiai_utils_path = sys.path[0]
        python_path = sys.executable
        cmd_template = "{PYTHON} {SCRIPT} {OPTIONS}"

        ### show category results
        results_script = pathlib.Path.joinpath(pathlib.Path(shiai_utils_path), "result_summary.py")
        patterns = [
            ".*",
            "Men|Women",
            "Men \\+.*",
            "Women \\+.*",
        ]

        for p in patterns:

            # set specific details of subprocess call
            options =  '--results-directory results/ --cat-pattern "{PATTERN}"'.format(PATTERN=p)
            cmd = cmd_template.format(PYTHON=python_path, SCRIPT=results_script, OPTIONS=options)

            # create button with script callback
            print(cmd)
            button = ft.Button(
                content=f"Category results {p}",
                on_click=self.run_python_in_cwd(cmd, pipe_to="kate -i"),
                icon=ft.Icons.LIST,
                elevation=1,
            )
            buttons.append(button)

        ### show group results
        options = "--results-directory results/ --no-cat-results --group-results --group-cert-template urkunde/urkunde_template.svg"
        cmd = cmd_template.format(PYTHON=python_path, SCRIPT=results_script, OPTIONS=options)

        button = ft.Button(
            content=f"Group results",
            on_click=self.run_python_in_cwd(cmd, pipe_to="kate -i"),
            icon=ft.Icons.LIST,
            elevation=1,
        )
        buttons.append(button)

        ### show medal needs
        medal_needs_script = pathlib.Path.joinpath(pathlib.Path(shiai_utils_path), "medal_needs.py")
        cmd = cmd_template.format(PYTHON=python_path, SCRIPT=medal_needs_script, OPTIONS="")

        button = ft.Button(
            content=f"Medal needs",
            on_click=self.run_python_in_cwd(cmd, open_file="medal_needs.md"),
            icon=ft.Icons.LIST,
            elevation=1,
        )
        buttons.append(button)

        input_field = ft.TextField(hint_text="regex for categories")
        def generate_report(e):
            pat = input_field.value
            options =  '--results-directory results/ --cat-pattern "{PATTERN}"'.format(PATTERN=pat)
            cmd = cmd_template.format(PYTHON=python_path, SCRIPT=results_script, OPTIONS=options)
            self.run_python_in_cwd(cmd, pipe_to="kate -i")(e)
        submit_button = ft.Button(
            content=f"Submit regex for cat results",
            on_click=generate_report,
            icon=ft.Icons.LIST,
            elevation=1,
        )

        # build page view
        info_text = ft.Text(value="Please first export the results from JUDOSHIAI to json!")
        content = ft.Column(controls=[*buttons, ft.Row([input_field, submit_button])])
        view_elements = [self.appbar, info_text, content]
        view = ft.View(controls=view_elements, route="/settings")
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

    def reset_matches(self, cat_id, match_numbers):

        async def reset_cat_matches(e):
            for match_id in sorted(match_numbers,reverse=True):
                self.reset_points(cat_id, match_id)
            self.page.views.clear()
            await self.set_category_view(cat_id)

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
    
    def open_reports(self):
        call = lambda e: asyncio.create_task(self.page.push_route("/reports"))
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

    def update_match_items(self, cat_id, items: list[Match]):
        async def update_function(e):
            # get all matches from judoshiai
            matches = await self.jsc.get_matches(cat_id)
            matches = {match: match_info for match, *match_info in matches}
            # if the matches changed too much, reload completely
            if {*matches.keys()} != {item.get_match_number() for item in items}:
                self.page.views.clear()
                await self.set_category_view(cat_id)
                return

            # get all competitors of the new matches
            comp_ids = {match[i] for match in matches.values() for i in (0, 1)}
            comps = {comp[0]: comp[1:] for comp in await self.jsc.get_competitors_info(comp_ids)}
            # update all match info displayed
            for item in items:
                match_number = item.get_match_number()
                b_info = comps[matches[match_number][0]]
                w_info = comps[matches[match_number][1]]
                b_points = matches[match_number][2]
                w_points = matches[match_number][3]
                item.update_comp(b_info[1], b_info[0], b_info[2], True)
                item.update_comp(w_info[1], w_info[0], w_info[2], False)
                item.update_points(b_points, True)
                item.update_points(w_points, False)
            self.page.update()

        return update_function

    async def match_items(self, cat_id, matches):
        # get all competitors for the matches
        comp_ids = {match[i] for match in matches for i in (1, 2)}
        comps = {comp[0]: comp[1:] for comp in await self.jsc.get_competitors_info(comp_ids)}

        # add a Match element to the UI for every match
        match_items: list[Match] = []
        for match_number, *match_info in matches:
            blue_info = comps[match_info[0]]
            white_info = comps[match_info[1]]

            match_items.append(Match(
                match_number,
                blue_info[1],
                blue_info[0],
                blue_info[2],
                match_info[2],
                white_info[1],
                white_info[0],
                white_info[2],
                match_info[3]
            ))

        # set refresh function and the on change functions for the Match objects
        update_function = self.update_match_items(cat_id, match_items)
        for match in match_items:
            match.set_refresh_function(update_function)
            match.set_on_change_function(
                self.update_points(cat_id, match, True, update_function),
                True
            )
            match.set_on_change_function(
                self.update_points(cat_id, match, False, update_function),
                False
            )

        return match_items

    def convert_and_simplify_score(self, score_string):
        # convert to format used by judoshiai (hex values represent IWYKS)
        if score_string == "10":
            return 0x10000
        elif score_string == "7":
            return 0x01000
        elif score_string == "5":
            return 0x00100
        elif score_string == "3":
            return 0x00010
        elif score_string == "1":
            return 0x00001
        else:
            return 0x00000

    def update_points(
        self,
        category_id: str,
        match: Match,
        is_blue: bool,
        refresh: Callable[[Any], Awaitable[None]]
    ) -> Callable[[Any], None]:
        async def update_db_points(e):
            score = self.convert_and_simplify_score(match.get_points(is_blue))
            if score == 0:
                return
            if is_blue:
                self.jsc.set_match_result(
                    category_id, match.get_match_number(), blue_score=score, white_score=0x0
                )
            else:
                self.jsc.set_match_result(
                    category_id, match.get_match_number(), blue_score=0x0, white_score=score
                )
            await refresh(None)

        return update_db_points

    def reset_points(self, category_id, match_id):
        self.jsc.set_match_result(
            category_id, match_id, blue_score=0x0, white_score=0x0
        )

    def run_python_in_cwd(self, cmd, pipe_to=None, open_file=""):
        if pipe_to:
            cmd = cmd + f" | {pipe_to}"
        
        def runner(e):
            print(cmd)

            result = subprocess.run(
                cmd,
                shell=True, 
                cwd=os.getcwd()
            )

            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)

            if open_file:
                result = subprocess.run(
                    f"kate {open_file}",
                    shell=True, 
                    capture_output=False,
                    cwd=os.getcwd()
                )

        return runner