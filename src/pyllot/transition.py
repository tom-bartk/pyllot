from collections.abc import Callable
from typing import Generic, TypeVar

from .direction import TransitionDirection

TState = TypeVar("TState")
"""Invariant type variable for a generic state."""

__all__ = ["Transition"]


class Transition(Generic[TState]):
    """The definition of transition from one screen to another.

    A transition describes a possible navigation from the source screen
    to the destination screen. If a router currently shows a screen named `source`,
    and the `should_transition` returns true, then the router will navigate to a screen
    named `destination`.
    """

    __slots__ = ("_source", "_destination", "_condition", "_direction")

    @property
    def source(self) -> str:
        """The name of the screen to transition from."""
        return self._source

    @property
    def destination(self) -> str:
        """The name of the screen to transition to."""
        return self._destination

    @property
    def direction(self) -> TransitionDirection:
        """The direction of the transition."""
        return self._direction

    _source: str
    _destination: str
    _direction: TransitionDirection
    _condition: Callable[[TState], bool]

    def __init__(
        self,
        source: str,
        destination: str,
        direction: TransitionDirection,
        condition: Callable[[TState], bool],
    ):
        """Initialize new transition.

        Args:
            source (str): The name of the source screen.
            destination (str): The name of the source screen.
            direction (TransitionDirection): The direction of the transition.
            condition (Callable[[TState], bool]): The predicate for this transition.
        """
        self._source = source
        self._destination = destination
        self._direction = direction
        self._condition = condition

    def should_transition(self, state: TState) -> bool:
        """Evaluate whether the transition should be perfromed given the `state`.

        Args:
            state (TState): The state to evaluate.

        Returns:
            True if transition should be perfromed; false otherwise.
        """
        return self._condition(state)

    def __repr__(self) -> str:
        return (
            f"Transition(source={self._source}, destination={self._destination}, "
            f"direction={self._direction.name}, condition={self._condition!r})"
        )
