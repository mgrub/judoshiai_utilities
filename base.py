import flet as ft


class MatchApp:
    def __init__(self, page: ft.Page, config_file="./config.json"):

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
            leading=ft.Icon(ft.icons.QUIZ),
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

        # create rows
        rows = [
            ft.ElevatedButton(
                text="Category",
                icon=ft.icons.CATEGORY,
                on_click=self.open_category(10000),
            )
        ]

        # create grid
        char_grid = ft.Row(
            [
                ft.Column(rows, expand=True),
            ],
            scroll=ft.ScrollMode.AUTO,
        )

        view_elements = [self.appbar, char_grid]

        view = ft.View(
            "/",
            view_elements,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        )
        self.page.views.append(view)

    def set_category_view(self, cid):

        view = ft.View(
            f"/category/{cid}",
            [
                self.appbar,
                ft.Text(f"{cid}", size=30, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton(
                    text="Back", icon=ft.icons.ARROW_BACK, on_click=self.open_home
                ),
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
            on_click=self.init_user_storage,
            icon=ft.icons.RESTART_ALT,
        )
        view_elements = [self.appbar, button_reset]
        view = ft.View("/settings", view_elements)
        self.page.views.append(view)

    def description_box(self, content=""):
        c = ft.Container(
            content=ft.Text(content, weight=ft.FontWeight.BOLD),
            margin=0,
            padding=0,
            alignment=ft.alignment.center,
            bgcolor=ft.colors.with_opacity(0.0, ft.colors.WHITE),
            opacity=100,
            width=5 * self.char_box_size,
            height=self.char_box_size,
        )
        return c

    def good_box(self, char: str = "A"):
        c = ft.Container(
            content=ft.Text(char, size=25),
            margin=0,
            padding=0,
            alignment=ft.alignment.center,
            bgcolor=ft.colors.GREEN_100,
            width=self.char_box_size,
            height=self.char_box_size,
            border=ft.border.all(2, ft.colors.GREEN_200),
            border_radius=8,
        )
        return c

    def view_pop(self, e):
        print("View pop:", e.view)
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.page.go(top_view.route)

    def open_category(self, cid):
        def open_cid(e):
            self.page.go(f"/category/{cid}")

        return open_cid

    def store_answer(self, qid):
        print(qid)

        def store_answer_qid(e):
            self.page.client_storage.set(qid, e.control.value)

        return store_answer_qid

    def open_home(self, e):
        self.page.go("/")

    def open_about(self, e):
        self.page.go("/about")

    def open_settings(self, e):
        self.page.go("/settings")

    def row_container_hover(self, e):
        e.control.bgcolor = ft.colors.LIGHT_BLUE_50 if e.data == "true" else ""
        e.control.update()
