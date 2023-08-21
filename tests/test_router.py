from collections.abc import Callable
from unittest.mock import Mock, PropertyMock, create_autospec

import pytest

from src.pyllot import (
    Router,
    ScreenBase,
    ScreenPresenting,
    ScreensFactoryBase,
    Transition,
    TransitionDirection,
)
from src.pyllot._stack import _NavigationStack


class State:
    pass


@pytest.fixture()
def create_screen() -> Callable[[str | None], ScreenBase]:
    def wrapped(name: str | None = None) -> ScreenBase:
        screen = create_autospec(ScreenBase)
        type(screen).screen_name = PropertyMock(return_value=name or "foo")
        return screen

    return wrapped


@pytest.fixture()
def initial_screen(create_screen) -> ScreenBase:
    return create_screen("initial")


@pytest.fixture()
def presenter() -> ScreenPresenting[ScreenBase]:
    return create_autospec(ScreenPresenting)


@pytest.fixture()
def navigation_stack(initial_screen) -> _NavigationStack[ScreenBase]:
    stack = create_autospec(_NavigationStack)

    def push(screen: ScreenBase) -> ScreenBase | None:
        return screen

    def pop(destination: str) -> ScreenBase | None:
        return None

    def peek() -> ScreenBase:
        return initial_screen

    stack.push = Mock(side_effect=push)
    stack.pop = Mock(side_effect=pop)
    stack.peek = Mock(side_effect=peek)
    return stack


@pytest.fixture()
def create_screens_factory(
    initial_screen,
) -> Callable[[ScreenBase | None], ScreensFactoryBase]:
    def wrapped(will_return: ScreenBase | None = None) -> ScreensFactoryBase:
        screens_factory = create_autospec(ScreensFactoryBase)

        def create(screen_name: str) -> ScreenBase:
            return will_return or initial_screen

        screens_factory.create = Mock(side_effect=create)
        return screens_factory

    return wrapped


@pytest.fixture()
def create_transition() -> (
    Callable[
        [str | None, str | None, TransitionDirection | None, bool | None],
        Transition[State],
    ]
):
    def wrapped(
        source: str | None = None,
        destination: str | None = None,
        direction: TransitionDirection | None = None,
        should_transition: bool | None = None,
    ) -> Transition[State]:
        transition = create_autospec(Transition)
        transition.source = source or ""
        transition.destination = destination or ""
        transition.direction = direction or TransitionDirection.PUSH
        transition.should_transition = Mock(return_value=should_transition or False)
        return transition

    return wrapped


@pytest.fixture()
def create_push_transition(
    create_transition,
) -> Callable[[str | None, str | None, bool | None], Transition[State]]:
    def wrapped(
        source: str | None = None,
        destination: str | None = None,
        should_transition: bool | None = None,
    ) -> Transition[State]:
        return create_transition(
            source, destination, TransitionDirection.PUSH, should_transition
        )

    return wrapped


@pytest.fixture()
def create_pop_transition(
    create_transition,
) -> Callable[[str | None, str | None, bool | None], Transition[State]]:
    def wrapped(
        source: str | None = None,
        destination: str | None = None,
        should_transition: bool | None = None,
    ) -> Transition[State]:
        return create_transition(
            source, destination, TransitionDirection.POP, should_transition
        )

    return wrapped


@pytest.fixture()
def create_sut(
    create_screens_factory, presenter, navigation_stack, initial_screen
) -> Callable[[ScreensFactoryBase | None, ScreenBase | None], Router[State, ScreenBase],]:
    def wrapped(
        factory: ScreensFactoryBase | None = None,
        initial: ScreenBase | None = None,
    ) -> Router:
        router: Router[State, ScreenBase] = Router(
            initial_screen=initial or initial_screen,
            presenter=presenter,
            screens_factory=factory or create_screens_factory(),
        )
        router._navigation_stack = navigation_stack
        return router

    return wrapped


class TestPushTransition:
    def test_when_valid_transition_found__creates_screen_using_factory_with_destination_name(  # noqa: E501
        self, create_sut, create_push_transition, create_screens_factory
    ):
        screens_factory = create_screens_factory()
        sut = create_sut(factory=screens_factory)
        sut.add_transition(
            create_push_transition(
                source="initial", destination="foo", should_transition=True
            )
        )

        sut.on_state(Mock())

        screens_factory.create.assert_called_once_with(screen_name="foo")

    def test_when_valid_transition_found__pushes_created_screen_on_navigation_stack(
        self,
        create_push_transition,
        create_screen,
        create_screens_factory,
        create_sut,
        navigation_stack,
    ):
        expected_screen = create_screen("foo")
        sut = create_sut(factory=create_screens_factory(will_return=expected_screen))
        sut.add_transition(
            create_push_transition(
                source="initial", destination="bar", should_transition=True
            )
        )

        sut.on_state(Mock())

        sut._navigation_stack.push.assert_called_once_with(expected_screen)

    def test_when_no_valid_transition_found__does_not_create_new_screen(
        self, create_push_transition, create_screen, create_screens_factory, create_sut
    ):
        screens_factory = create_screens_factory()
        sut = create_sut(factory=screens_factory)
        sut.add_transition(create_push_transition(should_transition=False))

        sut.on_state(Mock())

        screens_factory.create.assert_not_called()

    def test_when_no_valid_transition_found__does_not_push_anything_on_navigation_stack(
        self,
        create_push_transition,
        create_screen,
        create_screens_factory,
        create_sut,
        navigation_stack,
    ):
        sut = create_sut(
            factory=create_screens_factory(will_return=create_screen("foo")),
        )
        sut.add_transition(
            create_push_transition(
                source="initial", destination="foo", should_transition=False
            )
        )

        sut.on_state(Mock())

        sut._navigation_stack.push.assert_not_called()


class TestPopTransition:
    def test_when_valid_transition_found__pops_to_destination_from_navigation_stack(  # noqa: E501
        self, create_sut, create_pop_transition, create_screen, navigation_stack
    ):
        initial = create_screen("foo")
        expected_screen = create_screen("initial")
        navigation_stack.pop = Mock(return_value=expected_screen)
        navigation_stack.peek = Mock(return_value=initial)
        sut = create_sut(initial=initial)
        sut.add_transition(
            create_pop_transition(
                source="foo", destination="initial", should_transition=True
            )
        )

        sut.on_state(Mock())

        sut._navigation_stack.pop.assert_called_once_with(destination="initial")

    def test_when_no_valid_transition_found__does_not_pops_anything_from_navigation_stack(
        self,
        create_pop_transition,
        create_sut,
        create_screen,
        create_screens_factory,
        navigation_stack,
    ):
        sut = create_sut(factory=create_screens_factory(will_return=create_screen("foo")))
        sut.add_transition(
            create_pop_transition(
                source="initial", destination="foo", should_transition=False
            )
        )

        sut.on_state(Mock())

        sut._navigation_stack.pop.assert_not_called()


class TestOnState:
    def test_when_multiple_valid_transitions_found__performs_one_added_first(
        self,
        create_sut,
        create_push_transition,
        create_screens_factory,
        create_screen,
        navigation_stack,
    ):
        expected_screen = create_screen("bar")
        sut = create_sut(factory=create_screens_factory(will_return=expected_screen))
        sut.add_transition(
            create_push_transition(
                source="initial", destination="bar", should_transition=True
            )
        )
        sut.add_transition(
            create_push_transition(
                source="initial", destination="foo", should_transition=True
            )
        )

        sut.on_state(Mock())

        sut._navigation_stack.push.assert_called_once_with(expected_screen)

    def test_when_multiple_transitions_matching_source_found__performs_first_valid(
        self,
        create_sut,
        create_push_transition,
        create_screen,
        create_screens_factory,
        navigation_stack,
    ):
        expected_screen = create_screen("bar")
        screens_factory = create_screens_factory(will_return=expected_screen)
        sut = create_sut(factory=screens_factory)
        sut.add_transition(
            create_push_transition(
                source="initial", destination="foo", should_transition=False
            )
        )
        sut.add_transition(
            create_push_transition(
                source="initial", destination="bar", should_transition=True
            )
        )
        sut.add_transition(
            create_push_transition(
                source="initial", destination="baz", should_transition=True
            )
        )

        sut.on_state(Mock())

        sut._navigation_stack.push.assert_called_once_with(expected_screen)


class TestCurrentScreen:
    def test_returns_result_of_peeking_at_navigation_stack(
        self, create_sut, create_screen, navigation_stack
    ):
        expected_screen = create_screen("bar")
        navigation_stack.peek = Mock(return_value=expected_screen)

        sut = create_sut()

        assert sut.current_screen == expected_screen
