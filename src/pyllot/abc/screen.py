from abc import ABC, abstractmethod

__all__ = ["ScreenBase"]


class ScreenBase(ABC):
    """Represents an abstract screen of the application.

    A screen is the root widget of some standalone part of the application.
    Every subclass of the screen should have a unique name to ensure
    predictability of transitions. When a transition occurs, both the source
    and the destination screen will have their lifecycle methods called:

    * `will_present` - called on destination before presenting,
    * `did_present` - called on destination after presenting,
    * `will_disappear` - called on source before presenting the destination.

    """

    __slots__ = ()

    @property
    @abstractmethod
    def screen_name(self) -> str:
        """The name of the screen."""

    @abstractmethod
    def will_present(self) -> None:
        """Lifecycle method called before the presenter presents the screen."""

    @abstractmethod
    def did_present(self) -> None:
        """Lifecycle method called right after the presenter presents the screen."""

    @abstractmethod
    def will_disappear(self) -> None:
        """Lifecycle method called before it gets replaced by another screen."""
