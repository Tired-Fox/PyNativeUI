import platform

if platform.system() == "Windows":
    from native_ui.win import Window as WINDOW
else:
    raise ImportError(f"NativeUI is not implemented for the current platform ({platform.system()})")

