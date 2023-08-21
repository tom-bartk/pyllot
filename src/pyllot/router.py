from typing import Generic, TypeVar

from ._stack import _NavigationStack
from .abc import ScreenBase, ScreenPresenting, ScreensFactoryBase
from .direction import TransitionDirection
from .transition import Transition

TState = TypeVar("TState")
"""Invariant type variable for a generic state."""

TScreen = TypeVar("TScreen", bound=ScreenBase, covariant=True)
"""Covariant type variable bound by `ScreenBase`."""

__all__ = ["Router"]


class Router(Generic[TState, TScreen]):
    """Performs transitions between screens.

    The router is the main object that manages the transitions between screens.

    It's designed as a finite-state machine, where nodes are the screens,
    and the transitions are represented by the `Transition` objects.

    Navigation is triggered whenever the application's state changes, and one of the
    registered transitions evaluates it's predicate as true.

    Tip:
        The `on_state(self, state: TState) -> None` signature matches
        the `pydepot.StoreSubscriber[TState]` from the
        [`pydepot`](https://pydepot.tombartk.com) package.
        Pyllot works great with the state managed by the `pydepot.Store`.
    """

    __slots__ = ("_navigation_stack", "_screens_factory", "_transitions", "__weakref__")

    @property
    def current_screen(self) -> TScreen:
        """The currently displayed screen."""
        return self._navigation_stack.peek()

    def __init__(
        self,
        initial_screen: TScreen,
        presenter: ScreenPresenting[TScreen],
        screens_factory: ScreensFactoryBase[TScreen],
    ):
        """Initialize new router with a initial screen, presenter and screens factory.

        Args:
            initial_screen (TScreen): The initial screen to put on the stack.
            presenter (ScreenPresenting[TScreen]): The presenter of the screens.
            screens_factory (ScreensFactoryBase[TScreen]): The screens factory for
                creating screens at runtime.
        """
        self._navigation_stack: _NavigationStack[TScreen] = _NavigationStack(
            presenter=presenter, initial_screen=initial_screen
        )
        self._screens_factory: ScreensFactoryBase[TScreen] = screens_factory
        self._transitions: list[Transition[TState]] = []

    def add_transition(self, transition: Transition[TState]) -> None:
        """Add a possible transition.

        When the `on_state` method is called with a new state, all transitions that
        have the source equal to the current screen are evaluated using
        `should_transition`. The first transition that evaluates to true is performed.

        Args:
            transition (Transition[TState]): The transition to add.
        """
        self._transitions.append(transition)

    def on_state(self, state: TState) -> None:
        """Try to perform a transition given a new state.

        Finds all transitions that have the source equal to the current screen,
        and performs the first transition that evaluates the `should_transition` as true.

        This method is best used as a subscriber callback to some state publisher.

        Args:
            state (TState): The new state.
        """
        if transition := self._find_valid_transition(state):
            match transition.direction:
                case TransitionDirection.PUSH:
                    self._navigation_stack.push(
                        self._screens_factory.create(screen_name=transition.destination)
                    )
                case TransitionDirection.POP:
                    self._navigation_stack.pop(destination=transition.destination)

    def _find_valid_transition(self, state: TState) -> Transition[TState] | None:
        current_screen_name: str = self._navigation_stack.peek().screen_name
        return next(
            (
                transition
                for transition in self._transitions
                if transition.source == current_screen_name
                and transition.should_transition(state)
            ),
            None,
        )
