from typing import Literal, TypedDict
from ctypes.wintypes import RGB, HDC, BOOL, RECT, BYTE
from win32con import HS_DIAGCROSS

from win32gui import CreateHatchBrush, CreateSolidBrush

PAINTSTRUCT = tuple[HDC, BOOL, RECT, BOOL, BOOL, BYTE]
PyGdiHANDLE = tuple[int, PAINTSTRUCT]

__all__ = [
    "RGB",
    "HEX"
]

def HEX(value: str) -> int:
    value.lstrip("#") 
    if len(value) == 3:
        value = f"{value[0]*2}{value[1]*2}{value[2]*2}"

    value = f"00{value[4:6]}{value[2:4]}{value[0:2]}" 
    return int(value, 16) 

class BrushConfig(TypedDict, total=False):
    hatch: int 

class Brush:
    @staticmethod
    def create(_type: Literal["hatch", "solid"], color: int, config: BrushConfig|None = None) -> PyGdiHANDLE:
        return getattr(Brush, f"_{_type}_")(color, config or {})

    @staticmethod
    def _solid_(color: int, _: BrushConfig):
        return CreateSolidBrush(color)

    @staticmethod
    def _hatch_(color: int, config: BrushConfig):
        return CreateHatchBrush(config.get("hatch", HS_DIAGCROSS), color)

def brush(_type: Literal["hatch", "solid"], color: int, pattern: int = HS_DIAGCROSS) -> PyGdiHANDLE:
    return Brush.create(_type, color, {"hatch": pattern})

