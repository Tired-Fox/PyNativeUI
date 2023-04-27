from typing import Literal, TypeAlias, TypedDict

from win32con import (
    DT_BOTTOM,
    DT_CENTER,
    DT_LEFT,
    DT_RIGHT,
    DT_SINGLELINE,
    DT_TOP,
    DT_VCENTER,
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
    from native_ui.win.color import brush, RGB, HEX

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
        "align": Literal["start", "center", "end"] | Default,
        "justify": Literal["start", "center", "end"] | Default,
        "gap": int | Default,
        "padding": int | tuple[int, int] | tuple[int, int, int, int] | Default,
        "width": int | float | Default,
        "height": int | float | Default,
        "left": int | float | Default,
        "right": int | float | Default,
        "top": int | float | Default,
        "bottom": int | float | Default,
        "border": Literal["none", "single", "thick"] | Default,
        "background": Brush | Default,
        "color": str | tuple[int, int, int],
        "z-order": Literal["on-top", "default"] | Default,
    },
    total=False,
)


def style(style: dict):
    return {
        "align": DEFAULT,
        "justify": DEFAULT,
        "gap": 0,
        "padding": (0, 0, 0, 0),
        "width": DEFAULT,
        "height": DEFAULT,
        "left": DEFAULT,
        "right": DEFAULT,
        "top": DEFAULT,
        "bottom": DEFAULT,
        "border": DEFAULT,
        "background": DEFAULT,
        "color": "000",
        "z-order": DEFAULT,
        **(style or {}),
    }
