import win32con

from native_ui import Window, run, icon
from native_ui.color import HEX, brush
from native_ui.popup import message_box, ButtonLayout, Icon, MessageReturn
from native_ui.window import Hatch


def prompt_quit(hwnd) -> bool:
    return (
        message_box(hwnd, "Quit Application", "Are you sure?", ButtonLayout.OkCancel)
        == MessageReturn.Ok
    )


if __name__ == "__main__":
    
    if (
        message_box(
            body="Run the hello world window?",
            button_layout=ButtonLayout.YesNo,
            icon=Icon.Info,
        )
        == MessageReturn.Yes
    ):
        win = Window(
            ico="python.ico",
            background=brush("hatch", HEX("C3C3C3"), {"hatch": Hatch.DCROSS}),
            bind={
                "close": prompt_quit
            }
        )

        run(win)
