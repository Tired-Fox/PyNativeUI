from __future__ import annotations
from operator import itemgetter
from ctypes import pointer
from ctypes.wintypes import RECT

from typing import Literal, TypedDict
from win32api import GetSystemMetrics, GetWindowLong
from win32con import (
    BS_DEFPUSHBUTTON,
    DT_CALCRECT,
    GWL_HINSTANCE,
    SS_CENTER,
    WS_BORDER,
    WS_CHILD,
    WS_VISIBLE,
)
from win32gui import CreateWindow, DrawText, GetDC

caption_h = GetSystemMetrics(4)


class Component:
    def __init__(
        self,
        _style: StyleDict | None = None,
        parent=None,
    ):
        self.style = style(_style)
        self.parent = parent
        self.dimensions = (20, 10)
        self.pos = (0, 0)

    def init(self):
        if self.parent is None:
            raise ValueError(
                f"Expected {self.__class__.__name__} parent, but None was provided."
            )


def calc_text_size(text: str, parent) -> tuple[int, int]:
    rect: tuple[int, int, int, int] = DrawText(
        GetDC(parent.h_wnd), text, len(text), (0, 0, 0, 0), DT_CALCRECT
    )[1]
    #       left      right     top     bottom
    return rect[2] - rect[0], rect[3] - rect[1]


class Button(Component):
    def __init__(self, parent, text: str, style: StyleDict | None):
        super().__init__(style, parent)
        self.text = text

    def calc_size(self) -> tuple[int, int]:
        # specified width or percent of parent or text size
        isize = calc_text_size(self.text, self.parent)
        if isinstance(self.style["width"], float):
            width = self.parent.dimensions[0] * self.style["width"]
        else:
            width = self.style["width"]

        # specified height or percent of parent or text size
        if isinstance(self.style["height"], float):
            height = self.parent.dimensions[0] * self.style["height"]
        else:
            height = self.style["height"]
        return width, height

    def calc_pos(self) -> tuple[int, int]:
        # padding
        if isinstance(self.parent.style["padding"], tuple):
            if len(self.parent.style["padding"]) == 2:
                # top right bottom left
                padding = (
                    self.parent.style["padding"][0],
                    self.parent.style["padding"][1],
                    self.parent.style["padding"][0],
                    self.parent.style["padding"][1],
                )
            elif len(self.parent.style["padding"]) == 4:
                padding = self.parent.style["padding"]
            else:
                padding = (0, 0, 0, 0)
        else:
            padding = tuple([self.parent.style["padding"] for _ in range(4)])

        left, right, top, bottom = itemgetter("left", "right", "top", "bottom")(
            self.style
        )


        # left right percent
        if left != 0:
            x = left + padding[3]
        elif right != 0:
            x = self.parent.pos[0] + self.parent.dimensions[0] - right - padding[1] - self.dimensions[0]
        else:
            justify = self.parent.style["justify"]
            x = padding[1]

        # top bottom percent
        if top != 0:
            y = top + padding[0]
        elif bottom != 0:
            y = self.parent.dimensions[1] - bottom - padding[2] - self.dimensions[1] - caption_h
            print(self.parent.dimensions, y, self.dimensions[1])
        else:
            align = self.parent.style["align"]
            y = padding[0]

        return x, y

    def init(self):
        super().init()

        self.dimensions = self.calc_size()
        self.pos = self.calc_pos()
        print(self.dimensions)
        print(self.pos)

        return CreateWindow(
            "BUTTON",
            self.text,
            WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
            self.pos[0],
            self.pos[1],
            self.dimensions[0],
            self.dimensions[1],
            self.parent.h_wnd,
            0,
            GetWindowLong(self.parent.h_wnd, GWL_HINSTANCE),
            None,
        )


class Text(Component):
    def init(self):
        super().init()

        return CreateWindow(
            "STATIC",
            self.text,
            WS_VISIBLE | WS_CHILD | WS_BORDER | SS_CENTER,
            self.ipos[0],
            self.ipos[1],
            self.idim[0],
            self.idim[1],
            self.parent.h_wnd,
            0,
            GetWindowLong(self.parent.h_wnd, GWL_HINSTANCE),
            None,
        )


class StyleDict(TypedDict, total=False):
    align: Literal["start", "center", "end"]
    """Alignment the children of the window/container vertically."""
    justify: Literal["start", "center", "end"]
    """Align children of the window/container horizontally."""
    gap: int
    """Gap between children inside of the window/container."""
    padding: int | tuple[int, int] | tuple[int, int, int, int]
    """Padding inside of the container."""
    width: int | float
    """Width of the container in pixels. If value is a float then it is a percent of the parents width."""
    height: int | float
    """Height of the container in pixels. If value is a float then it is a percent of the parents height."""
    left: int | float
    """Distance from parents left side in pixels. Padding is added on top of this value."""
    right: int | float
    """Distance from parents right side in pixels. Padding is added on top of this value."""
    top: int | float
    """Distance from parents top side in pixels. Padding is added on top of this value."""
    bottom: int | float
    """Distance from parents bottom side in pixels. Padding is added on top of this value."""


def style(style: StyleDict | None):
    return {
        "align": "start",
        "justify": "start",
        "gap": 0,
        "padding": (0, 0, 0, 0),
        "width": 20,
        "height": 10,
        "left": 0,
        "right": 0,
        "top": 0,
        "bottom": 0,
        **(style or {}),
    }


def center(current: int, parent: int, offset: int = 0):
    return (parent // 2) - (current // 2) + offset


class VBOX(Component):
    def __init__(self, *components: Component, _style: StyleDict | None = None):
        super().__init__(style)
        self.components = components
        self.style = style(_style)

    def init(self):
        super().init()
        current = (0, 0)

        gap = self.style["gap"]
        width = 0
        height = 0
        start_x = self.parent.dimensions[0] // 2
        for child in self.components:
            child.parent = self.parent

            # TODO: Update position of each child
            x, y = child.ipos
            if "align" in self.style:
                y = center(child.dimensions[1], child.parent.dimensions[1])
            if "justify" in self.style:
                x = 0

            child.init()
