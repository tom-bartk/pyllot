from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from .screen import ScreenBase

TScreen = TypeVar("TScreen", bound=ScreenBase, covariant=True)
"""Covariant type variable bound by `ScreenBase`."""

__all__ = ["ScreensFactoryBase"]


class ScreensFactoryBase(Generic[TScreen], ABC):
    """Factory creating new screens by their name.

    The factory solves a problem of initializing new screens at runtime - whenever
    a push transition occurs.

    Typical usage is to subclass it, and provide all necessary dependencies needed
    for instantiating new screens.

    Example:
        ```python3
        from pyllot import ScreenBase, ScreensFactoryBase


        class MyScreen(ScreenBase):
            ...


        class HomeScreen(MyScreen):
            @property
            def screen_name(self) -> str:
                return "home"


        class VideoPlayerScreen(MyScreen):
            @property
            def screen_name(self) -> str:
                return "video_player"


        class MyScreensFactory(ScreensFactoryBase[MyScreen]):
            def create(self, screen_name: str) -> MyScreen:
                match screen_name:
                    case "home":
                        return HomeScreen()
                    case "video_player":
                        return VideoPlayerScreen()
                    case _:
                        raise NotImplementedError
        ```
    """

    __slots__ = ()

    @abstractmethod
    def create(self, screen_name: str) -> TScreen:
        """Create new screen named `screen_name`.

        Args:
            screen_name (str): The name of the screen to create.

        Returns:
            TScreen: The created screen.
        """
