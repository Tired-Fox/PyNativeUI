from native_ui.kit.win import Window as Win

if __name__ == "__main__":
    with Win(
        title="Layout",
        ico="python.ico",
        style={
            "width": 1000,
            "height": 800,
            "padding": (5, 10),
            "background": ("hatch", "c3c3c3", "dcross"),
        },
    ) as win:
        win.Button("Previous", style={"width": 500, "height": 300, "margin": (5, 0)})
        win.Button(
            "Current",
            style={
                "width": 0.4,
                "height": 120,
            },
        )
        win.Text(
            "Sample text to text layout system",
            style={
                "border": "single",
                "justify": "center",
                "align": "center",
                "overflow": "none",
                "width": 1.0,
                "height": 32,
            },
        )
