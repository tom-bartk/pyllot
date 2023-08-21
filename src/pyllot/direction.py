from enum import IntEnum

__all__ = ["TransitionDirection"]


class TransitionDirection(IntEnum):
    """The specification of how the transition should be performed."""

    PUSH = 1
    """Push the destination screen on top of the navigation stack."""

    POP = 2
    """Pop every screen from the navigation stack that is on top of the destination."""
