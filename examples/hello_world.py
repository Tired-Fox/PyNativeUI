from native_ui.kit.win import Window, run, handler
from native_ui.kit.win.popup import message_box, ButtonLayout, Icon, MessageReturn


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


# Styling is based on css. The format is the same.
# This allows for easier and intuitive styling.
# There will be a custom css based styling language for this library called Native
# Cascading Style Sheet or (NCSS).
# This language will be used in the outer scoped custom markup langauge that
# allows for html style creating of windows
#
# <link type="stylesheet" href="style.ncss">
# <window>
#   <button onclick="<some callback>" style="<ncss styles>">Hello World!</button>
# </window>

if __name__ == "__main__":
    if (
        message_box(
            body="Run the hello world window?",
            button_layout=ButtonLayout.YesNo,
            icon=Icon.Info,
        )
        == MessageReturn.Yes
    ):
        # CSS Equivelant:
        #
        # window {
        #   icon: python.ico;
        #   width: 800px;
        #   height: 400px;
        #   background: hatch #c3c3c3 tangent
        # }
        win = Window(
            title="Hello World",
            klass="HelloWorld",
            bind={"close": prompt_quit},
            ico="python.ico",
            style={
                "width": 800,
                "height": 400,
                "background": ("hatch", "c3c3c3", "tangent"),
            },
        )

        # CSS Equivelant:
        #
        # window {
        #   icon: python.ico;
        #   width: 400px;
        #   height: 200px;
        #   background: #F0F;
        #   z-order: on-top;
        # }

        run(win)

    with Window(
        title="Hello World",
        klass="HelloWorld2",
        ico="python.ico",
        style={
            "width": 400,
            "height": 200,
            "background": "F0F",
            "z-order": "on-top",
        },
    ) as window:
        window.Button("Hello World", {
            "width": 150,
            "height": 50,
            "justify": "center",
            "align": "center"
        })
        window.Text(
            "Some Text",
            {
                "width": 150,
                "height": 100,
                "justify": "end",
                "align": "end",
                "border": "single"
            },
        )
        window.Text(
            "right",
            {
                "top": -50,
                "color": "FFF"
            }
        )
