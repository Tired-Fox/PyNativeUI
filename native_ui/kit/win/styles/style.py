from functools import cache
from typing import Any, Literal, TypeAlias, TypedDict

from ..data import Rect

from win32con import (
    DT_BOTTOM,
    DT_CENTER,
    DT_END_ELLIPSIS,
    DT_LEFT,
    DT_RIGHT,
    DT_SINGLELINE,
    DT_TOP,
    DT_VCENTER,
    DT_WORDBREAK,
    HS_BDIAGONAL,
    HS_CROSS,
    HS_DIAGCROSS,
    HS_FDIAGONAL,
    HS_HORIZONTAL,
    HS_VERTICAL,
    HWND_NOTOPMOST,
    HWND_TOPMOST,
    WS_BORDER,
    WS_MAXIMIZE,
    WS_MINIMIZE,
    WS_THICKFRAME,
)

BrushType: TypeAlias = Literal["solid", "hatch"]
BrushColor: TypeAlias = tuple[int, int, int] | str
BrushPattern: TypeAlias = Literal[
    "dcross", "cross", "vertical", "horizontal", "tangent", "diagnol"
]
Brush: TypeAlias = (
    tuple[BrushType, BrushColor, BrushPattern]
    | tuple[BrushType, BrushColor]
    | BrushColor
)
"""Examples: 
    - ("solid", "#e3e3e3")
    - ("solid" (244, 12, 153))
    - ("hatch" "F0F")
    - ("hatch", "F0F","dcross")
"""


class Default:
    def __bool__(self):
        return False


DEFAULT = Default()

str_to_style = {
    "border": {"single": WS_BORDER, "thick": WS_THICKFRAME, "default": 0},
    "justify": {
        "start": DT_LEFT,
        "center": DT_CENTER,
        "end": DT_RIGHT,
        "default": DT_LEFT,
    },
    "align": {
        "start": DT_TOP,
        "center": DT_VCENTER | DT_SINGLELINE,
        "end": DT_BOTTOM | DT_SINGLELINE,
        "default": DT_TOP,
    },
    "on-open": {"minimize": WS_MINIMIZE, "maximize": WS_MAXIMIZE, "default": 0},
    "z-order": {"on-top": HWND_TOPMOST, "default": HWND_NOTOPMOST},
    "overflow": {
        "break": DT_WORDBREAK,
        "ellipse": DT_END_ELLIPSIS,
        "none": 0
    },
}

hatch_pattern = {
    "dcross": HS_DIAGCROSS,
    "cross": HS_CROSS,
    "vertical": HS_VERTICAL,
    "horizontal": HS_HORIZONTAL,
    "tangent": HS_FDIAGONAL,
    "diagnol": HS_BDIAGONAL,
}


def to_style(key, value):
    try:
        if value == DEFAULT:
            return str_to_style[key]["default"]
        return str_to_style[key][value]
    except:
        return 0


def parse_background(bkg: Brush):
    from native_ui.kit.win.color import brush, RGB, HEX

    if bkg == DEFAULT:
        return brush("solid", HEX("FFF"))

    if isinstance(bkg, str):
        return brush("solid", HEX(bkg))
    elif isinstance(bkg[0], int):
        return brush("solid", RGB(*bkg))
    else:
        # type color pattern
        _type, color = bkg[:2]
        pattern = "dcross"
        if len(bkg) > 2:
            pattern = bkg[2]

        return brush(
            _type,
            HEX(color) if isinstance(color, str) else RGB(*color),
            hatch_pattern[pattern],
        )


StyleDict = TypedDict(
    "StyleDict",
    {
        "align": Literal["start", "center", "end"],
        "justify": Literal["start", "center", "end"],
        "gap": int,
        "padding": int
        | tuple[int, int]
        | tuple[int, int, int]
        | tuple[int, int, int, int],
        "margin": int
        | tuple[int, int]
        | tuple[int, int, int]
        | tuple[int, int, int, int],
        "width": int | float,
        "height": int | float,
        "left": int | float,
        "right": int | float,
        "top": int | float,
        "bottom": int | float,
        "border": Literal["none", "single", "thick"],
        "background": Brush,
        "color": str | tuple[int, int, int],
        "z-order": Literal["on-top", "default"],
        "overflow": Literal["break", "ellipse", "none"],
    },
    total=False,
)

Stylesheet = dict[str, StyleDict]

top = int
left = int
right = int
bottom = int


class Styled:
    def __init__(self, style: StyleDict):
        self.style = style

    def __getitem__(self, key: str):
        return self.style[key]

    def __contains__(self, key: str) -> bool:
        return key in self.style

    def get(self, key, default: Any = ...):
        if default == ...:
            return self.style.get(key)
        return self.style.get(key, default)

    @cache
    def padding(self, parent: Rect) -> tuple[top, right, bottom, left]:
        if "padding" not in self.style:
            return (0, 0, 0, 0)

        if isinstance(self.style["padding"], tuple):
            # top right bottom left
            p = self.style["padding"]
            if len(p) == 2:
                return (
                    size(p[0] or 0, parent.height),
                    size(p[1] or 0, parent.width),
                    size(p[0], parent.height),
                    size(p[1], parent.width),
                )
            if len(p) == 3:
                return (
                    size(p[0], parent.height),
                    size(p[1], parent.width),
                    size(p[2], parent.height),
                    size(p[1], parent.width),
                )
            if len(p) == 4:
                return (
                    size(p[0], parent.height),
                    size(p[1], parent.width),
                    size(p[2], parent.height),
                    size(p[3], parent.width),
                )
        else:
            p = self.style["padding"]
            return (
                size(p, parent.height),
                size(p, parent.width),
                size(p, parent.height),
                size(p, parent.width),
            )

        return (0, 0, 0, 0)

    @cache
    def margin(self, parent: Rect) -> tuple[top, right, bottom, left]:
        if "margin" not in self.style:
            return (0, 0, 0, 0)

        if isinstance(self.style["margin"], tuple):
            # top right bottom left
            p = self.style["margin"]
            if len(p) == 2:
                return (
                    size(p[0], parent.height),
                    size(p[1], parent.width),
                    size(p[0], parent.height),
                    size(p[1], parent.width),
                )
            if len(p) == 3:
                return (
                    size(p[0], parent.height),
                    size(p[1], parent.width),
                    size(p[2], parent.height),
                    size(p[1], parent.width),
                )
            if len(p) == 4:
                return (
                    size(p[0], parent.height),
                    size(p[1], parent.width),
                    size(p[2], parent.height),
                    size(p[3], parent.width),
                )
        else:
            p = self.style["margin"]
            return (
                size(p, parent.height),
                size(p, parent.width),
                size(p, parent.height),
                size(p, parent.width),
            )

        return (0, 0, 0, 0)


def size(value, parent: int) -> int:
    if isinstance(value, float):
        s = round(parent * value)
        if s >= parent:
            s = parent
        return s
    return value
