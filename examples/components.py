from ctypes.wintypes import RECT
from win32api import GetSystemMetrics
from win32con import WS_CHILD, WS_VISIBLE, WS_BORDER, SS_CENTER, GWL_HINSTANCE, BS_DEFPUSHBUTTON
from win32gui import CreateWindow, GetWindowLong, GetWindowRect
from native_ui.win import Window, HEX, Hatch, brush

def dimensions(window) -> tuple[int, int]:
    rect = GetWindowRect(window.h_wnd)
    return rect[2] - rect[0], rect[3] - rect[1]

def center(current: int, parent: int, offset: int = 0):
    return (parent//2) - (current//2) + offset

def relative_center(other: int, parent: int, offset: int):
    return (parent//2) + (other//2) + offset

if __name__ == "__main__":
    message = Window(
        title="Hello World",
        ico="python.ico",
        klass="PyNativeMessage",
        size=(500, 300),
        background=brush("hatch", HEX("F0F"), pattern=Hatch.DCROSS),
    )

    width, height = dimensions(message)
    ttb_h = GetSystemMetrics(4) 

    CreateWindow(
        "STATIC",
        "Hello World",
        WS_CHILD | WS_VISIBLE | WS_BORDER | SS_CENTER,
        center(100, width),
        center(50, height, -ttb_h),
        100,
        50,
        message.h_wnd,
        0,
        GetWindowLong(message.h_wnd, GWL_HINSTANCE),
        None,
    )

    button = CreateWindow(
        "BUTTON",
        "OK",
        WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
        center(100, width),
        relative_center(50, height, -ttb_h+10),
        100,
        25,
        message.h_wnd,
        0,
        GetWindowLong(message.h_wnd, GWL_HINSTANCE),
        None,
    )

    message.open()
