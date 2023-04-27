from win32gui import MessageBox
from ctypes.wintypes import HWND

from win32con import (
    MB_ABORTRETRYIGNORE,
    MB_HELP,
    MB_OK,
    MB_OKCANCEL,
    MB_RETRYCANCEL,
    MB_YESNO,
    MB_YESNOCANCEL,
    MB_ICONINFORMATION,
    MB_ICONWARNING,
    MB_ICONQUESTION,
    MB_ICONERROR,
    IDABORT,
    IDCANCEL,
    IDIGNORE,
    IDNO,
    IDOK,
    IDRETRY,
    IDYES,
)


class ButtonLayout:
    AbortRetryIgnore = MB_ABORTRETRYIGNORE
    CancelTryContinue = 0x00000006
    Help = MB_HELP
    Ok = MB_OK
    OkCancel = MB_OKCANCEL
    RetryCancel = MB_RETRYCANCEL
    YesNo = MB_YESNO
    YesNoCancel = MB_YESNOCANCEL


class Icon:
    Info = MB_ICONINFORMATION
    Warning = MB_ICONWARNING
    Question = MB_ICONQUESTION
    Error = MB_ICONERROR


class MessageReturn:
    Abort = IDABORT
    Cancel = IDCANCEL
    Continue = 11
    Ignore = IDIGNORE
    No = IDNO
    Ok = IDOK
    Retry = IDRETRY
    TryAgain = 10
    Yes = IDYES


def message_box(
    parent: HWND | None = None,
    title: str = "",
    body: str = "",
    button_layout: int = 0,
    icon: int = 0,
):
    """Create a message box with a title, content text, icon, and buttons.

    Args:
        parent (HWND | None): The windows handle of the parent window or None for a standalone message box.
        title (str): The title of the message box. Defaults to ''.
        body (str): Message that goes in the message box. Defaults to ''.
        button_layout (int): Button layout that should be used. Use the ButtonLayout class for defined values.
            Defaults to ButtonLayout.Ok == 0.
        icon (int): Icon to display with the message box. Defaults to no icon == 0.

    Returns:
        int: The message return of what button was pressed. Use MessageReturn to compare against defined values.
    """
    return MessageBox(parent, body, title, button_layout | icon)
