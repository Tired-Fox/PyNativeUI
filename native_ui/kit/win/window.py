from __future__ import annotations
from contextlib import contextmanager
from pathlib import Path
from traceback import print_stack
from types import FunctionType
from typing import Any, Iterator, Literal, TypeAlias, Callable, TypedDict
from badges import wraps
from win32.lib.win32con import CS_HREDRAW, CS_VREDRAW, CW_USEDEFAULT
import win32api
import win32gui
import win32con

from native_ui.kit.win.component import Component, Button, Text
from native_ui.kit.win.styles import (
    StyleDict,
    to_style,
    parse_background,
    DEFAULT,
    Styled,
)
from native_ui.kit.win.data import Rect

from ctypes import GetLastError, WinError, windll, pointer
from ctypes.wintypes import HICON, MSG, HWND

user32 = windll.user32

# from .color import HEX, Brush, PyGdiHANDLE

Handler: TypeAlias = Callable[[HWND], bool]
Event: TypeAlias = Literal["close", "destroy"]


class WindowHandlers:
    """Assignable handlers for different window events."""

    close: Handler | None = None
    destroy: Handler | None = None

    def __setitem__(self, key, value):
        if isinstance(value, FunctionType):
            setattr(self, key, value)
        else:
            raise TypeError("Window handlers may only be python callable methods")


class WindowHandlerDict(TypedDict, total=False):
    close: Handler
    destroy: Handler


def icon(path: str) -> HICON:
    """Helper to load an image as an ico."""
    return win32gui.LoadImage(
        0,
        path,
        win32con.IMAGE_ICON,
        0,
        0,
        win32con.LR_LOADFROMFILE
        | win32con.LR_SHARED
        | win32con.LR_LOADTRANSPARENT
        | win32con.LR_DEFAULTSIZE,
    )


class Window:
    """Window context object. Creates a WNDCLASS with the passed in values.

    Args:
        title (str): The window's title.
        ico (str): The path to a custom window icon. Must be a `.ico` file.
        size (tuple[int, int]): Initial size of the window. Packed tuple of (width, height).
        background (PyGdiHandle): The brush to paint the background with. Use
            `brush` or `Brush.create`
        klass (str): Window class (Label)
        bind (WindowHandlerDict): Dict of event bindings. The keys are defined events while
            the value is a method that returns true or false and is passed the
            current windows handle.
        minimize (bool): Whether the window can be minimized.
        maximize (bool): Whether the window can be maximized.
        minimized (bool): Whether the window should start minimized.
        maximized (bool): Whether the window should start maximized.
        alwasy_on_top (bool): Whether the window should start as alwasy on top.
    """

    def __init__(
        self,
        *,
        title: str = "",
        klass: str | None = None,
        bind: WindowHandlerDict | None = None,
        ico: str = "",
        on_open: Literal["minimize", "maximize"] = DEFAULT,
        style: StyleDict | None = None,
    ):
        win32gui.InitCommonControls()
        message_map = {
            win32con.WM_DESTROY: self.on_destroy,
            win32con.WM_ERASEBKGND: self.on_erasebkgnd,
            win32con.WM_CLOSE: self.on_close,
            win32con.WM_SIZE: self.on_resize,
        }
        self.children = []
        self.h_inst = win32api.GetModuleHandle(None)
        self.style = Styled(style or {})
        self.handlers = WindowHandlers()
        if bind is not None:
            for key, value in bind.items():
                self.bind_event(key, value)

        ico_path = Path(ico)
        if ico != "" and (not ico_path.exists() or ico_path.suffix != ".ico"):
            raise ValueError(
                f"Can only apply '.ico' files as icons in window, was {ico_path.suffix!r}"
            )

        self.icon = icon(ico) if ico != "" else 0
        self.background = parse_background(self.style["background"])
        self.always_on_top = to_style("z-order", self.style.get("z-order", DEFAULT))
        self.init_size = (
            self.style.get("width", None) or CW_USEDEFAULT,
            self.style.get("height", None) or CW_USEDEFAULT,
        )

        wc = win32gui.WNDCLASS()
        wc.hIcon = self.icon
        # wc.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
        wc.lpfnWndProc = message_map
        wc.lpszClassName = klass or f"PyNativeUI-{title}"
        wc.style = CS_VREDRAW | CS_HREDRAW
        
        win32gui.RegisterClass(wc)

        w_style = win32con.WS_TILEDWINDOW
        w_style |= to_style("on-open", on_open)

        self.h_wnd = win32gui.CreateWindow(
            wc.lpszClassName,
            title,
            w_style,
            win32con.CW_USEDEFAULT,
            win32con.CW_USEDEFAULT,
            self.style["width"] or CW_USEDEFAULT,
            self.style["height"] or CW_USEDEFAULT,
            0,
            0,
            self.h_inst,
            None,
        )

        win32gui.SetWindowPos(
            self.h_wnd,
            self.always_on_top,
            0,
            0,
            0,
            0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
        )

        self._is_alive_ = True
        # left top right bottom
        rect = win32gui.GetWindowRect(self.h_wnd)
        self.caption_height = win32api.GetSystemMetrics(4)
        self.rect = Rect(
            0,
            self.caption_height,
            self.style.get("width", rect[2] - rect[0]),
            self.style.get("height", rect[3] - rect[1]),
        )

    def update(self):
        previous = (Rect(0, 0, 0, 0), Styled({}))
        for child in self.children:
            child.update(previous=previous, parent=(self.rect, self.style))
            previous = (child.rect, child.style)

    def __enter__(self) -> Window:
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.open()

    def Button(self, text: str, style: StyleDict|None = None)-> Button:
        cbutton = Button(self, text, style)
        self.children.append(cbutton)
        return cbutton

    def Text(self, text: str, style: StyleDict | None = None) -> Text:
        ctext = Text(self, text, style)
        self.children.append(ctext)
        return ctext

    def is_alive(self) -> bool:
        return self._is_alive_

    def bind_event(self, event: Event, handler: Callable[[HWND], bool]):
        """Add an event handler to the window instance."""
        self.handlers[event] = handler

    def open(self, translate: bool = False, errors: bool = False):
        """Open and run the current window."""
        win32gui.ShowWindow(self.h_wnd, win32con.SW_SHOW)
        for child in self.children:
            child.init()
        self.update()

        with msg() as message:
            while self.is_alive():
                mr = user32.GetMessageA(message, self.h_wnd, 0, 0)
                if errors and mr == -1:
                    raise WinError(GetLastError())
                if translate:
                    user32.TranslateMessage(message)
                user32.DispatchMessageA(message)

    def layout(self, *children: Component):
        self.children.extend(children)
        for child in children:
            child.parent = self
            child.init()

    def on_erasebkgnd(self, h_wnd, *_):
        # Draw defined background
        hdc, ps = win32gui.BeginPaint(h_wnd)
        win32gui.FillRect(hdc, ps[2], self.background)
        hdc = win32gui.EndPaint(h_wnd, ps)

        return True

    def on_close(self, h_wnd, *_):
        if self.handlers.close is not None:
            if self.handlers.close(h_wnd) == True:
                win32gui.DestroyWindow(h_wnd)
        else:
            win32gui.DestroyWindow(h_wnd)
        return True

    def on_resize(self, h_wnd, message, wparam, lparam):
        width = win32gui.LOWORD(lparam)
        height = win32gui.HIWORD(lparam)

        self.caption_height = win32api.GetSystemMetrics(4)
        self.rect = Rect(
            0,
            0,
            win32gui.LOWORD(lparam),
            win32gui.HIWORD(lparam),
        )

        self.update()
        return win32gui.DefWindowProc(h_wnd, message, wparam, lparam)

    def on_destroy(self, h_wnd, *_):
        """What happend when a window is destroyed"""

        if self.handlers.destroy is not None:
            self.handlers.destroy(h_wnd)
        self._is_alive_ = False
        return True


def run(*windows: Window, errors: bool = False):
    """Run a given window. This will also create a loop watching for messages and
    dispatching messages to the window.
    """

    for window in windows:
        if window is not None:
            win32gui.ShowWindow(window.h_wnd, win32con.SW_SHOW)

    with msg() as message:
        while any(window.is_alive() for window in windows):
            mr = user32.GetMessageA(message, None, 0, 0)
            if mr == -1 and errors:
                raise WinError(GetLastError())
            user32.TranslateMessage(message)
            user32.DispatchMessageA(message)


class Missing:
    """Custom missing object to define a missing arg that can also be None."""


MISSING = Missing()


def handler(expect: Any = MISSING):
    """Create an event handler that takes a windows handle and executes code.
    The wrapped method should return a bool of True == success or False == fail
    or any value with the 'expect' argument provided. With the 'expect' arugment provided
    the returned value from the wrapped method is compared with the 'expect' value

    Args:
        expect (Any): The value that means the wrapped methods return is truthly

    Returns:
        bool: Whether the wrapped method is a success return or not
    """

    def wrapper(func: Callable[[HWND], Any]) -> Handler:
        @wraps(func)
        def inner(hwnd: HWND) -> bool:
            result = func(hwnd)
            if expect == MISSING:
                if not isinstance(result, bool):
                    print_stack()
                    print(
                        f"TypeError: Expected handler to return a bool value, found {type(result).__name__!r}"
                    )
                    win32gui.PostQuitMessage(0)
                return result
            return result == expect

        return inner

    return wrapper


@contextmanager
def msg() -> Iterator:
    message = MSG()
    message_p = pointer(message)
    yield message_p
