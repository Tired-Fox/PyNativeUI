from native_ui.win import Window, run, HEX, brush, Hatch, handler
from native_ui.win.popup import message_box, ButtonLayout, Icon, MessageReturn


@handler(expect=MessageReturn.Ok)
def prompt_quit(hwnd) -> bool:
    """Promt the user before quiting. Allow them to cancel quitting the window."""
    return message_box(
        hwnd,
        title="Quit",
        body="Are you sure you want to quit?",
        button_layout=ButtonLayout.OkCancel,
        icon=Icon.Warning,
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
            title="Hello World",
            ico="python.ico",
            klass="HelloWorld",
            size=(800, 400),
            background=brush("hatch", HEX("C3C3C3"), {"hatch": Hatch.DCROSS}),
            minimize=False,
            bind={"close": prompt_quit},
        )

        run(win)
