from abc import abstractmethod
from typing import Protocol, TypeVar

from .screen import ScreenBase

TScreen = TypeVar("TScreen", bound=ScreenBase, contravariant=True)
"""Contravariant type variable bound by `ScreenBase`."""

__all__ = ["ScreenPresenting"]


class ScreenPresenting(Protocol[TScreen]):
    """Displays a screen to the end user..

    The exact implementation will depend on the presentation framework of the application.
    Typically, screens are presented in a wrapped container widget, for example:

    * `ttk.Frame` for `tkinter`,
    * `WidgetWrap` for `urwid`,
    * `Gtk.Window` for `Gtk3`,
    * `DynamicContainer` for `prompt_toolkit`.

    Any object implementing the `present(screen: TScreen) -> None` method
    is a valid presenter.
    """

    __slots__ = ()

    @abstractmethod
    def present(self, screen: TScreen) -> None:
        """Present a screen.

        Args:
            screen (TScreen): Screen to present.
        """
