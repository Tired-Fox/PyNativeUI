from pathlib import Path
from types import FunctionType
from typing import TYPE_CHECKING, Literal, TypeAlias, Callable, TypedDict
import win32api
import win32gui
import win32con

if TYPE_CHECKING:
    from _win32typing import PyGdiHANDLE

from ctypes import windll, pointer
from ctypes.wintypes import HICON, MSG, HWND, WPARAM, LPARAM

from .styles import Hatch
from .color import HEX, Brush, PyGdiHANDLE

Handler: TypeAlias = Callable[[HWND], bool]
Event: TypeAlias = Literal["close"]


class WindowHandlers:
    close: Handler | None = None

    def __setitem__(self, key, value):
        if isinstance(value, FunctionType):
            setattr(self, key, value)
        else:
            raise TypeError("Window handlers may only be python callable methods")


class WindowHandlerDict(TypedDict, total=False):
    close: Handler


def icon(path: str) -> HICON:
    return win32gui.LoadImage(
        0,
        path,
        win32con.IMAGE_ICON,
        0,
        0,
        win32con.LR_LOADFROMFILE
        | win32con.LR_SHARED
        | win32con.LR_LOADTRANSPARENT
        | win32con.LR_DEFAULTSIZE
    )


class Window:
    def __init__(
        self,
        *,
        title: str = "",
        ico: str = "",
        size: tuple[int, int] = (win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT),
        background: PyGdiHANDLE = Brush.create("solid", HEX("FFF")),
        klass: str = "PythonNativeUI",
        bind: WindowHandlerDict | None = None,
    ):
        win32gui.InitCommonControls()
        self.h_inst = win32api.GetModuleHandle(None)
        self.handlers = WindowHandlers()
        if bind is not None:
            for key, value in bind.items():
                self.bind_event(key, value)
        self.background = background
        ico_path = Path(ico)
        if not ico_path.exists() or ico_path.suffix != ".ico":
            raise ValueError(f"Can only apply '.ico' files as icons in window, was {ico_path.suffix!r}")
        self.icon = icon(ico) if ico != "" else 0

        className = "PythonNativeWnd"

        message_map = {
            win32con.WM_DESTROY: self.OnDestroy,
            win32con.WM_CLOSE: self.OnClose,
            win32con.WM_PAINT: self.OnPaint,
        }

        wc = win32gui.WNDCLASS()
        wc.hIcon = self.icon
        wc.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
        wc.lpfnWndProc = message_map
        wc.lpszClassName = klass
        win32gui.RegisterClass(wc)
        style = win32con.WS_TILEDWINDOW | win32con.WS_VISIBLE

        self.h_wnd = win32gui.CreateWindow(
            klass,
            title,
            style,
            win32con.CW_USEDEFAULT,
            win32con.CW_USEDEFAULT,
            size[0],
            size[1],
            0,
            0,
            self.h_inst,
            None,
        )

    def bind_event(self, event: Event, handler: Callable[[HWND], bool]):
        """Add an event handler to the window instance."""
        self.handlers[event] = handler

    def OnCreate(self, hwnd: HWND, message: int, wparam: WPARAM, lparam: LPARAM):
        print("OnCreate")
        win32gui.SetWindowPos(
            self.h_wnd,
            None,
            800,
            400,
            0,
            0,
            win32con.SWP_NOACTIVATE | win32con.SWP_NOMOVE | win32con.SWP_NOZORDER,
        )
        return True

    def OnPaint(self, hwnd: HWND, message: int, wparam: WPARAM, lparam: LPARAM):
        hdc, ps = win32gui.BeginPaint(hwnd)
        win32gui.FillRect(hdc, ps[2], self.background)
        hdc = win32gui.EndPaint(hwnd, ps)

        return True

    def OnClose(self, hwnd, message, wparam, lparam):
        if self.handlers.close is not None:
            print("ONCLOSE", result := self.handlers.close(hwnd))
            if result == True:
                win32gui.DestroyWindow(hwnd)
        else:
            win32gui.DestroyWindow(hwnd)
        return True

    def OnDestroy(self, hwnd, message, wparam, lparam):
        win32gui.PostQuitMessage(0)
        return True


def run(window: Window):
    msg = MSG()
    lpmsg = pointer(msg)

    print("Entering message loop")
    while windll.user32.GetMessageA(lpmsg, None, 0, 0) != 0:
        windll.user32.TranslateMessage(lpmsg)
        windll.user32.DispatchMessageA(lpmsg)

    print("done.")
