"""
Windows portion of the native API. This module contains wrappers around win32 API's
using pywin32 and ctypes. The abstractions can be used as is or with the higher level
parent module that creates an API that can be used with macOs, Windows, and Linux.
"""
__version__ = "0.1.0"

from .window import Window, run, handler
from .color import HEX, RGB, brush

__all__ = [
    "Window",
    "run",
    "HEX",
    "RGB",
    "brush",
    "handler"
]
