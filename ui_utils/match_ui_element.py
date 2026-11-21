from typing import Any, Awaitable, Callable

import flet as ft


class Match(ft.ResponsiveRow):
    """
    A flet ResponsiveRow object that displays all information on a match and lets the user set the
    result of the match and offers a refresh button with variable on_change function.
    """

    def __init__(
        self,
        match_number: str,
        b_first_name: str,
        b_surname: str,
        b_club: str,
        b_points: str,
        w_first_name: str,
        w_surname: str,
        w_club: str,
        w_points: str
    ) -> None:
        """
        Creates the initial version of this object. The arguments are self-explanatory.

        Note that as is the refresh button and on_change function of the RadioGroups are not set
        only after calling __init__.
        """
        # create empty inner objects and store relevant references.
        self.match_number = match_number
        self.b_name, self.b_club, b_comp_box = self._empty_comp_box(True)
        self.b_points, b_point_radio = self._empty_res_radio()
        self.w_name, self.w_club, w_comp_box = self._empty_comp_box(False)
        self.w_points, w_point_radio = self._empty_res_radio()
        self.refresh_button = ft.IconButton(icon=ft.Icons.REFRESH)

        # fill the inner objects with data
        self.update_comp(b_first_name, b_surname, b_club, True)
        self.update_points(b_points, True)
        self.update_comp(w_first_name, w_surname, w_club, False)
        self.update_points(w_points, False)

        # create outer objects and complete init
        opacity = 1.0 if b_surname != "empty" and w_surname != "empty" else 0.3
        content = [
            ft.Container(
                content=ft.Column([ft.Text(match_number, size=22), self.refresh_button]),
                col={"sm": 12, "md": 1, "xxl": 0.5},
                opacity=opacity,
            ),
            ft.Container(
                content=ft.Row([b_comp_box, b_point_radio]),
                col={"sm": 12, "md": 10, "xxl": 5},
                opacity=opacity,
            ),
            ft.Container(
                content=ft.Row([w_comp_box, w_point_radio]),
                col={"sm": 12, "md": 10, "xxl": 5},
                opacity=opacity,
            ),
            ft.Divider(),
        ]
        super().__init__(controls=content, alignment=ft.MainAxisAlignment.END)

    def _empty_comp_box(self, is_blue: bool) -> tuple[ft.Text, ft.Text, ft.Container]:
        """
        Creates an empty box for the competitor information.

        Args:
            is_blue (bool): Whether or not the competitor will be blue or white.
        Returns:
            tuple[ft.Text, ft.Text, ft.Container]: The text field of the name and of the club as
                well as the container of the box.
        """
        name = ft.Text("", size=30)
        club = ft.Text("", size=22)

        return name, club, ft.Container(
            content=ft.Column([name, club]),
            border=ft.border.Border().all(1, ft.Colors.GREY_300),
            margin=10,
            padding=10,
            alignment=ft.alignment.Alignment.CENTER_LEFT,
            bgcolor=ft.Colors.BLUE_300 if is_blue else ft.Colors.WHITE,
            height=100,
            border_radius=10,
            expand=3,
        )

    def _empty_res_radio(self) -> tuple[ft.RadioGroup, ft.Container]:
        """
        Creates an container for the RadioGroup used to display and change the result of the match.

        Returns:
            tuple[ft.RadioGroup, ft.Container]: The RadioGroup for input and output as well as the
                container of the containing it.
        """
        radio_group = ft.RadioGroup(
            ft.Row(
                [
                    ft.Column(
                        [ft.Text("0"), ft.Radio(value="0", label="")],
                        alignment=ft.alignment.Alignment.CENTER,
                    ),
                    ft.Column(
                        [ft.Text("1"), ft.Radio(value="1", label="")],
                        alignment=ft.alignment.Alignment.CENTER,
                    ),
                    ft.Column(
                        [ft.Text("5"), ft.Radio(value="5", label="")],
                        alignment=ft.alignment.Alignment.CENTER,
                    ),
                    ft.Column(
                        [ft.Text("7"), ft.Radio(value="7", label="")],
                        alignment=ft.alignment.Alignment.CENTER,
                    ),
                    ft.Column(
                        [ft.Text("10"), ft.Radio(value="10", label="")],
                        alignment=ft.alignment.Alignment.CENTER,
                    )
                ]
            )
        )

        radio_container = ft.Container(
            content=radio_group,
            expand=1,
        )
        return radio_group, radio_container

    def set_refresh_function(self, ref_func: Callable[[Any], Awaitable[None]]) -> None:
        """
        Set the function called by the refresh button on click to the given function.

        Args:
            ref_func (Callable[[Any], Awaitable[None]]): The new on click function.
        """
        self.refresh_button.on_click = ref_func

    def set_on_change_function(
        self, on_change_func: Callable[[Any], Awaitable[None]], is_blue: bool
    ) -> None:
        """
        Set the function called by the RadioGroup (associated with blue or white) on change to the
        given function.

        Args:
            on_change_func (Callable[[Any], Awaitable[None]]): The new on change function.
            is_blue (bool): Whether the function of the RadioGroup associated with blue or white is
                to be changed.
        """
        (self.b_points if is_blue else self.w_points).on_change = on_change_func

    def update_comp(self, first_name: str, surname: str, club: str, is_blue: bool) -> None:
        """
        Update the data of the Competitor box (associated with blue or white) with the given data.

        Args:
            first_name (str): clear
            surname (str): clear
            club (str): clear
            is_blue (bool): Whether to update the date of blue or white.
        """
        name_obj = self.b_name if is_blue else self.w_name
        club_obj = self.b_club if is_blue else self.w_club

        new_name = f"{first_name}, {surname}"
        new_club = f"({club})"
        if name_obj.value == new_name and club_obj.value == new_club:
            return
        name_obj.value = new_name
        club_obj.value = new_club

        opacity = 1.0 if self.b_name.value != ", empty" and self.w_name.value != ", empty" else 0.3
        for item in getattr(self, "controls", []):
            if item.opacity != opacity:
                item.opacity = opacity

    def update_points(self, points: str, is_blue: bool) -> None:
        """
        Programmatically update the data of the RadioGroup (associated with blue or white) with the
        given points.

        Args:
            points (str): clear
            is_blue (bool): Whether to update the points of blue or white.
        """
        (self.b_points if is_blue else self.w_points).value = points

    def get_match_number(self) -> str:
        return self.match_number[:]

    def get_points(self, is_blue: bool) -> str:
        return (self.b_points if is_blue else self.w_points).value[:]
