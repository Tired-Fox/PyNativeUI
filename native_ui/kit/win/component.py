from __future__ import annotations
from win32.lib.win32con import WM_DRAWITEM, WM_NOTIFY, WS_CHILDWINDOW

from win32api import RGB, GetWindowLong
from win32con import (
    BS_OWNERDRAW,
    DT_CALCRECT,
    GWL_HINSTANCE,
    GWL_WNDPROC,
    TRANSPARENT,
    WM_PAINT,
    WS_CHILD,
    WS_VISIBLE,
)
from win32gui import (
    BeginPaint,
    CreateWindow,
    DefWindowProc,
    DrawText,
    EndPaint,
    FillRect,
    GetClientRect,
    GetDC,
    SetBkMode,
    SetTextColor,
    SetWindowLong,
)
from .styles import StyleDict, style as cstyle, to_style, parse_background
from .color import HEX


class Component:
    def __init__(
        self,
        style: StyleDict | None = None,
        parent=None,
    ):
        self.style = cstyle(style)
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
    def __init__(self, parent, text: str, style: StyleDict | None = None):
        super().__init__(style, parent)
        self.text = text

    def proc(self, hWnd, msg, wParam, lParam):
        if msg == WM_NOTIFY:
            print("BUTTON INTERACT")
            return True
        elif msg == WM_PAINT:
            hdc, ps = BeginPaint(hWnd)
            SetBkMode(hdc, TRANSPARENT)
            EndPaint(hWnd, ps)
            return True
        elif msg == WM_DRAWITEM:
            print("DRAW ITEM", wParam, lParam)
            return True
        else:
            return DefWindowProc(hWnd, msg, wParam, lParam)

    def init(self):
        super().init()

        text_size = calc_text_size(self.text, self.parent)

        width = self.style["width"] or text_size[0] + 8
        height = self.style["height"] or text_size[1] + 8

        wWrapper = CreateWindow(
            "STATIC",
            "",
            WS_VISIBLE | WS_CHILDWINDOW,
            0,
            0,
            width,
            height,
            self.parent.h_wnd,
            0,
            GetWindowLong(self.parent.h_wnd, GWL_HINSTANCE),
            None,
        )

        wButton = CreateWindow(
            "BUTTON",
            self.text,
            WS_VISIBLE | WS_CHILD | BS_OWNERDRAW,
            0,
            0,
            width,
            height,
            wWrapper,
            0,
            GetWindowLong(wWrapper, GWL_HINSTANCE),
            None,
        )

        SetWindowLong(wWrapper, GWL_WNDPROC, self.proc)

class Text(Component):
    def __init__(self, parent, text: str, style: StyleDict | None):
        super().__init__(style, parent)
        self.text = text

    def proc(self, hWnd, msg, wParam, lParam):
        if msg == WM_PAINT:
            hdc, ps = BeginPaint(hWnd)
            SetBkMode(hdc, TRANSPARENT)
            color = self.style["color"]
            SetTextColor(hdc, RGB(*color) if isinstance(color, tuple) else HEX(color))
            rect = GetClientRect(hWnd)
            style = (
                to_style("justify", self.style["justify"])
                | to_style("align", self.style["align"])
            )
            DrawText(
                hdc, self.text, len(self.text), rect, style
            )
            EndPaint(hWnd, ps)
            return True
        else:
            return DefWindowProc(hWnd, msg, wParam, lParam)

    def init(self):
        super().init()

        text_size = calc_text_size(self.text, self.parent)
        wText = CreateWindow(
            "STATIC",
            self.text,
            WS_VISIBLE | WS_CHILD | to_style("border", self.style["border"]),
            160,
            50 + (self.style["top"] or 0),
            self.style["width"] or text_size[0] + 4,
            self.style["height"] or text_size[1] + 2,
            self.parent.h_wnd,
            0,
            GetWindowLong(self.parent.h_wnd, GWL_HINSTANCE),
            None,
        )

        SetWindowLong(wText, GWL_WNDPROC, self.proc)


def center(current: int, parent: int, offset: int = 0):
    return (parent // 2) - (current // 2) + offset