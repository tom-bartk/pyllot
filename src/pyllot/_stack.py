from typing import Generic, TypeVar

from .abc import ScreenBase, ScreenPresenting

_TScreen = TypeVar("_TScreen", bound=ScreenBase)
"""Type variable bound by `ScreenBase`."""

__all__ = ["_NavigationStack"]


class _NavigationStack(Generic[_TScreen]):
    """The stack of pushed screens.

    The navigation stack is composed of a stack of screens that it manages,
    and a presenter that is notified whenever a screen is pushed or popped.
    """

    __slots__ = ("_presenter", "_stack")

    def __init__(
        self,
        presenter: ScreenPresenting[_TScreen],
        initial_screen: _TScreen,
    ):
        """Initialize new navigation stack with a presenter and initial screen.

        Args:
            initial_screen (_TScreen): The initial screen to put on the stack.
            presenter (ScreenPresenting[_TScreen]): The presenter of the screens.
        """
        self._presenter: ScreenPresenting[_TScreen] = presenter
        self._stack: list[_TScreen] = [initial_screen]

    def push(self, screen: _TScreen) -> _TScreen:
        """Push a screen on the stack.

        Args:
            screen (ScreenName): The screen to push.

        Returns:
            The destination screen.
        """
        self.peek().will_disappear()
        self._stack.append(screen)
        self._present(screen)
        return screen

    def pop(self, destination: str) -> _TScreen | None:
        """Pop to screen named `destination`.

        Args:
            destination (str): The name of the screen to pop to.

        Returns:
            The destination screen if transition was successful, `None` otherwise.
        """
        if screen := next((s for s in self._stack if s.screen_name == destination), None):
            self.peek().will_disappear()
            self._stack = self._stack[: self._stack.index(screen) + 1]
            self._present(screen)
            return screen
        return None

    def peek(self) -> _TScreen:
        """Get the screen that is on top of the stack.

        Returns:
            The screen on top of the stack.
        """
        return self._stack[-1]

    def _present(self, screen: _TScreen) -> None:
        screen.will_present()
        self._presenter.present(screen)
        screen.did_present()
