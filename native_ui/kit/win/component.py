from __future__ import annotations

import struct
from win32.lib.win32con import (
    BS_CHECKBOX,
    ODS_DEFAULT,
    ODS_FOCUS,
    ODS_SELECTED,
    PS_DASHDOTDOT,
    WM_DRAWITEM,
    WM_NOTIFY,
    WS_CHILDWINDOW,
)

from win32api import RGB, GetWindowLong
from win32con import (
    BS_FLAT,
    BS_GROUPBOX,
    BS_HOLLOW,
    BS_OWNERDRAW,
    BS_PUSHBUTTON,
    BS_RADIOBUTTON,
    DT_CALCRECT,
    DT_CENTER,
    DT_SINGLELINE,
    DT_VCENTER,
    GWL_EXSTYLE,
    GWL_HINSTANCE,
    GWL_WNDPROC,
    HWND_NOTOPMOST,
    NULL_BRUSH,
    ODS_HOTLIGHT,
    PS_DASHDOT,
    PS_DOT,
    TRANSPARENT,
    WM_ERASEBKGND,
    WM_NCPAINT,
    WM_PAINT,
    WS_BORDER,
    WS_CHILD,
    WS_EX_LAYERED,
    WS_EX_TRANSPARENT,
    WS_VISIBLE,
)
from win32gui import (
    BeginPaint,
    CreatePen,
    CreateSolidBrush,
    CreateWindow,
    DefWindowProc,
    DrawText,
    EndPaint,
    FillRect,
    FrameRect,
    GetClientRect,
    GetDC,
    GetStockObject,
    GetWindowRect,
    InvalidateRect,
    PyGetMemory,
    RedrawWindow,
    RoundRect,
    SelectObject,
    SetBkColor,
    SetBkMode,
    SetTextColor,
    SetWindowLong,
    SetWindowPos,
    UpdateWindow,
    ValidateRect,
)

from native_ui.kit.win.styles.style import parse_background
from .styles import StyleDict, to_style, Styled, size, DEFAULT
from .color import HEX
from .data import Rect


def clamp(value: int | float, _min: int | float, _max: int | float) -> int | float:
    """Clamp a number withing a range."""
    if value > _max:
        value = _max
    if value < _min:
        value = _min
    return value


class Component:
    def __init__(
        self,
        style: StyleDict | None = None,
        parent=None,
    ):
        self.style = Styled(style or {})
        self.parent = parent
        self.dimensions = (20, 10)
        self.pos = (0, 0)
        self.rect = Rect(0, 0, 0, 0)
        self.handle = 0

    def init(self):
        if self.parent is None:
            raise ValueError(
                f"Expected {self.__class__.__name__} parent, but None was provided."
            )

    def update_rect(self, rect: Rect):
        self.rect.update(rect)
        if self.handle != 0:
            SetWindowPos(
                self.handle,
                0,
                rect.left,
                rect.top,
                rect.width,
                rect.height,
                0,
            )

            InvalidateRect(self.handle, tuple(rect), True)

    def update(self):
        raise NotImplementedError(
            f"Expected component {self.__class__.__name__!r} to implement update()"
        )


def calc_text_size(text: str, parent) -> tuple[int, int]:
    rect: tuple[int, int, int, int] = DrawText(
        GetDC(parent.h_wnd), text, len(text), (0, 0, 0, 0), DT_CALCRECT
    )[1]
    #       left      right     top     bottom
    return rect[2] - rect[0], rect[3] - rect[1]


class DRAWITEMSTRUCT:
    """
    Values
        CtlType (uint): int
        CtlId (uint): int
        itemID (uint): int
        itemAction (uint): int
        itemState (uint): int
        hwndItem (HWND|void*): int
        hDC (HDC|void*): int
        rcItem (RECT): (int, int, int, int)
        itemData (ulong_ptr|void*): int
    """

    _fmt_ = "5i2P4iP"
    """ Stucture Values:

        CtlType (i): int
        CtlId (i): int
        itemID (i): int
        itemAction (i): int
        itemState (i): int
        hwndItem (P): void*
        hDC (P): void*
        rcItem (4i): (int, int, int, int)
        itemData (P): void*
    """

    def __init__(self, lParam):
        fmt = "5i2P4iP"
        data = struct.unpack(fmt, PyGetMemory(lParam, struct.calcsize(fmt)))

        self.CtlType = data[0]
        self.CtlId = data[1]
        self.itemID = data[2]
        self.itemAction = data[3]
        self.itemState = data[4]
        self.hwndItem = data[5]
        self.hDC = data[6]
        self.rcItem = Rect(*data[7:11])
        self.itemData = data[11]

    def __repr__(self) -> str:
        return (
            f"DRAWITEMSTRUCT{{"
            + f"CtlType={self.CtlType}, "
            + f"CtlId={self.CtlId}, "
            + f"itemID={self.itemID}, "
            + f"itemAction={self.itemAction}, "
            + f"itemState={self.itemState}, "
            + f"hwndItem={self.hwndItem}, "
            + f"hDC={self.hDC}, "
            + f"rcItem={self.rcItem}, "
            + f"itemData={self.itemData}"
            + "}}"
        )


class Button(Component):
    def __init__(self, parent, text: str, style: StyleDict | None = None):
        super().__init__(style, parent)
        self.text = text
        self.sub_handle = 0

    def proc(self, hWnd, msg, wParam, lParam):
        if msg == WM_NOTIFY:
            print("BUTTON INTERACT")
            return True
        elif msg in [WM_PAINT, WM_NCPAINT]:
            hdc, ps = BeginPaint(hWnd)
            SetBkMode(hdc, TRANSPARENT)
            EndPaint(hWnd, ps)
            return True
        else:
            return DefWindowProc(hWnd, msg, wParam, lParam)

    def calc_rect(
        self, previous: tuple[Rect, Styled], parent: tuple[Rect, Styled]
    ) -> Rect:
        rect = Rect(0, 0, 0, 0)

        ppad = parent[1].padding(parent[0])
        pmarg = previous[1].margin(parent[0])
        marg = self.style.margin(parent[0])
        text_size = calc_text_size(self.text, self.parent)

        c_width = parent[0].width - ppad[1] - ppad[3] - marg[3] - marg[1]
        width = size(
            self.style.get("width", text_size[0] + 8),
            # PERF: Subtract font size from width
            c_width,
        )

        width = size(self.style.get("width", text_size[0] + 8), c_width)
        # if self.style.get("overflow", None) in ["none", None] and isinstance(self.style.get("width", 0), float):
        #     width = clamp(width, text_size[0] + 8, c_width)

        if width >= c_width:
            rect.left = ppad[3] + marg[3]
        if "left" in self.style:
            rect.left = (
                ppad[3] + size(self.style.get("left", 0), parent[0].width) + marg[3]
            )
        elif "right" in self.style:
            rect.left = (
                parent[0].right - self.style.get("right", 0) - ppad[1] - width - marg[1]
            )
        else:
            rect.left = ppad[3] + marg[3]
        rect.right = rect.left + width

        c_height = parent[0].height - ppad[0] - ppad[2] - marg[0] - marg[2]
        height = size(
            self.style.get("height", text_size[1] + 8),
            c_height,
        )
        height = clamp(height, text_size[1], c_height)
        if "top" in self.style:
            rect.top = (
                ppad[0] + size(self.style.get("top", 0), parent[0].height) + marg[0]
            )
        elif "bottom" in self.style:
            rect.top = (
                parent[0].bottom
                - size(self.style.get("bottom", 0), parent[0].height)
                - ppad[2]
                - height
                - marg[2]
            )
        else:
            rect.top = previous[0].bottom + pmarg[2] + marg[0]
            if previous[0].bottom == 0:
                rect.top += ppad[0]
        rect.bottom = rect.top + height

        return rect

    def update(self, previous: tuple[Rect, Styled], parent: tuple[Rect, Styled]):
        rect = self.calc_rect(previous, parent)
        self.update_rect(rect)

    def update_rect(self, rect: Rect):
        super().update_rect(rect)
        norm_rect = rect.normalized
        if self.sub_handle != 0:
            SetWindowPos(
                self.sub_handle,
                0,
                norm_rect.left,
                norm_rect.top,
                norm_rect.width,
                norm_rect.height,
                0,
            )
            # RedrawWindow(self.sub_handle, tuple(self.rect), None, 0)
            InvalidateRect(self.sub_handle, tuple(self.rect), False)
            # UpdateWindow(self.sub_handle)

    def init(self):
        super().init()

        wWrapper = CreateWindow(
            "STATIC",
            "",
            WS_VISIBLE | WS_CHILD,
            0,
            0,
            0,
            0,
            self.parent.h_wnd,
            0,
            GetWindowLong(self.parent.h_wnd, GWL_HINSTANCE),
            None,
        )

        wButton = CreateWindow(
            "BUTTON",
            self.text,
            WS_VISIBLE | WS_CHILD | BS_PUSHBUTTON,
            0,
            0,
            0,
            0,
            wWrapper,
            0,
            GetWindowLong(wWrapper, GWL_HINSTANCE),
            None,
        )

        SetWindowLong(wWrapper, GWL_WNDPROC, self.proc)
        # SetWindowLong(wButton, GWL_WNDPROC, self.button_proc)

        self.handle = wWrapper
        self.sub_handle = wButton

        assert self.handle != 0
        assert self.sub_handle != 0


class Text(Component):
    def __init__(self, parent, text: str, style: StyleDict | None):
        super().__init__(style, parent)
        self.text = text

    def proc(self, hWnd, msg, wParam, lParam):
        if msg == WM_PAINT:
            hdc, ps = BeginPaint(hWnd)
            old_brush = None
            rect = Rect(*GetClientRect(hWnd))

            if self.style.get("background", "transparent") != "transparent":
                old_brush = SelectObject(hdc, parse_background(self.style.get("background")))
            else:
                old_brush = SelectObject(hdc, GetStockObject(NULL_BRUSH))

            pen = CreatePen(PS_DASHDOTDOT, 1, HEX("F0F"))
            old_pen = SelectObject(hdc, pen)

            SetBkMode(hdc, TRANSPARENT)
            if "border" in self.style:
                print("Draw border")
                RoundRect(hdc, *tuple(rect), rect.height, rect.height)
            color = self.style.get("color", "000")
            SetTextColor(hdc, RGB(*color) if isinstance(color, tuple) else HEX(color))

            style = to_style("justify", self.style.get("justify", DEFAULT))

            if "overflow" in self.style:
                style |= to_style("overflow", self.style.get("overflow"))
            if "overflow" not in self.style or self.style["overflow"] != "break":
                style |= to_style("align", self.style.get("align", DEFAULT))

            DrawText(hdc, self.text, len(self.text), tuple(rect), style)
            
            if old_brush is not None:
                SelectObject(hdc, old_brush)
            SelectObject(hdc, old_pen)
            EndPaint(hWnd, ps)
            return True
        else:
            return DefWindowProc(hWnd, msg, wParam, lParam)

    def calc_rect(
        self, previous: tuple[Rect, Styled], parent: tuple[Rect, Styled]
    ) -> Rect:
        rect = Rect(0, 0, 0, 0)

        ppad = parent[1].padding(parent[0])
        pmarg = previous[1].margin(parent[0])
        marg = self.style.margin(parent[0])
        text_size = calc_text_size(self.text, self.parent)

        c_width = parent[0].width - ppad[1] - ppad[3] - marg[3] - marg[1]
        width = size(
            self.style.get("width", text_size[0] + 8),
            # PERF: Subtract font size from width
            c_width,
        )

        width = size(self.style.get("width", text_size[0] + 8), c_width)
        if self.style.get("overflow", None) in ["none", None]:
            width = clamp(width, text_size[0] + 8, c_width)

        if width >= c_width:
            rect.left = ppad[3] + marg[3]
        if "left" in self.style:
            rect.left = (
                ppad[3] + size(self.style.get("left", 0), parent[0].width) + marg[3]
            )
        elif "right" in self.style:
            rect.left = (
                parent[0].right - self.style.get("right", 0) - ppad[1] - width - marg[1]
            )
        else:
            rect.left = ppad[3] + marg[3]
        rect.right = rect.left + width

        c_height = parent[0].height - ppad[0] - ppad[2] - marg[0] - marg[2]
        height = size(
            self.style.get("height", text_size[1] + 8),
            c_height,
        )
        height = clamp(height, text_size[1], c_height)
        if "top" in self.style:
            rect.top = (
                ppad[0] + size(self.style.get("top", 0), parent[0].height) + marg[0]
            )
        elif "bottom" in self.style:
            rect.top = (
                parent[0].bottom
                - size(self.style.get("bottom", 0), parent[0].height)
                - ppad[2]
                - height
                - marg[2]
            )
        else:
            rect.top = previous[0].bottom + pmarg[2] + marg[0]
            if previous[0].bottom == 0:
                rect.top += ppad[0]
        rect.bottom = rect.top + height

        return rect

    def update(self, previous: tuple[Rect, Styled], parent: tuple[Rect, Styled]):
        rect = self.calc_rect(previous, parent)
        self.update_rect(rect)

    def init(self):
        super().init()

        wText = CreateWindow(
            "STATIC",
            self.text,
            WS_VISIBLE | WS_CHILD,# | to_style("border", self.style["border"]),
            0,
            0,
            20,
            10,
            self.parent.h_wnd,
            0,
            GetWindowLong(self.parent.h_wnd, GWL_HINSTANCE),
            None,
        )

        SetWindowLong(wText, GWL_WNDPROC, self.proc)
        self.handle = wText


def center(current: int, parent: int, offset: int = 0):
    return (parent // 2) - (current // 2) + offset
