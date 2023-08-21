from collections.abc import Callable
from unittest.mock import Mock, PropertyMock, create_autospec

import pytest

from src.pyllot import ScreenBase, ScreenPresenting
from src.pyllot._stack import _NavigationStack


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
def screen_presenter() -> ScreenPresenting[ScreenBase]:
    return create_autospec(ScreenPresenting)


@pytest.fixture()
def create_sut(
    screen_presenter, initial_screen
) -> Callable[[ScreenBase | None], _NavigationStack[ScreenBase]]:
    def wrapped(initial: ScreenBase | None = None) -> _NavigationStack:
        return _NavigationStack(
            presenter=screen_presenter, initial_screen=initial or initial_screen
        )

    return wrapped


class TestPush:
    def test_returns_pushed_screen(self, create_sut, create_screen):
        expected_screen = create_screen("foo")
        sut = create_sut()

        result = sut.push(expected_screen)

        assert result == expected_screen

    def test_peek_returns_pushed_screen(self, create_sut, create_screen):
        expected_screen = create_screen("foo")
        sut = create_sut()

        sut.push(expected_screen)

        assert sut.peek() == expected_screen

    def test_calls_will_disappear_on_current_screen(
        self, create_sut, initial_screen, create_screen
    ):
        sut = create_sut(initial=initial_screen)

        sut.push(create_screen("foo"))

        initial_screen.will_disappear.assert_called_once()

    def test_calls_will_present_on_destination_screen_before_presenting(
        self, create_sut, create_screen, screen_presenter
    ):
        destination = create_screen("foo")

        def present(screen: ScreenBase) -> None:
            destination.will_present.assert_called_once()

        screen_presenter.present = Mock(side_effect=present)
        sut = create_sut()

        sut.push(destination)

    def test_presents_destination_screen_on_presenter(
        self, create_sut, create_screen, screen_presenter
    ):
        destination = create_screen("foo")
        sut = create_sut()

        sut.push(destination)

        screen_presenter.present.assert_called_once_with(destination)

    def test_calls_did_present_on_destination_screen_after_presenting(
        self, create_sut, create_screen, screen_presenter
    ):
        destination = create_screen("foo")

        def present(screen: ScreenBase) -> None:
            destination.did_present.assert_not_called()

        screen_presenter.present = Mock(side_effect=present)
        sut = create_sut()

        sut.push(destination)

        screen_presenter.present.assert_called_once()
        destination.did_present.assert_called_once()


class TestPop:
    def test_when_destination_is_on_stack__returns_destination_screen(
        self, create_sut, create_screen
    ):
        expected_screen = create_screen("initial")
        sut = create_sut(initial=expected_screen)
        sut.push(create_screen("foo"))

        result = sut.pop(destination="initial")

        assert result == expected_screen

    def test_when_destination_is_not_on_stack__returns_none(
        self, create_sut, create_screen
    ):
        expected_screen = create_screen("initial")
        sut = create_sut(initial=expected_screen)
        sut.push(create_screen("foo"))

        result = sut.pop(destination="bar")

        assert not result

    def test_when_destination_is_on_stack__peek_returns_destination_screen(
        self, create_sut, create_screen
    ):
        expected_screen = create_screen("initial")
        sut = create_sut(initial=expected_screen)
        sut.push(create_screen("foo"))

        sut.pop(destination="initial")

        assert sut.peek() == expected_screen

    def test_when_destination_is_on_stack__calls_will_disappear_on_current_screen(
        self, create_sut, create_screen
    ):
        foo_screen = create_screen("foo")
        sut = create_sut(initial=create_screen("initial"))
        sut.push(foo_screen)
        foo_screen.reset_mock()

        sut.pop(destination="initial")

        foo_screen.will_disappear.assert_called_once()

    def test_when_destination_is_on_stack__calls_will_present_on_destination_screen_before_presenting(  # noqa: E501
        self, create_sut, create_screen, screen_presenter
    ):
        foo_screen = create_screen("foo")
        initial_screen = create_screen("initial")
        sut = create_sut(initial=initial_screen)
        sut.push(foo_screen)
        foo_screen.reset_mock()
        initial_screen.reset_mock()

        initial_screen.will_present.assert_not_called()

        def present(screen: ScreenBase) -> None:
            initial_screen.will_present.assert_called_once()

        screen_presenter.present = Mock(side_effect=present)
        sut.pop(destination="initial")

    def test_when_destination_is_on_stack__presents_destination_screen_on_presenter(  # noqa: E501
        self, create_sut, create_screen, screen_presenter
    ):
        foo_screen = create_screen("foo")
        initial_screen = create_screen("initial")
        sut = create_sut(initial=initial_screen)
        sut.push(foo_screen)
        foo_screen.reset_mock()
        initial_screen.reset_mock()
        screen_presenter.reset_mock()

        sut.pop(destination="initial")

        screen_presenter.present.assert_called_once_with(initial_screen)

    def test_when_destination_is_on_stack__calls_did_present_on_destination_screen_after_presenting(  # noqa: E501
        self, create_sut, create_screen, screen_presenter
    ):
        foo_screen = create_screen("foo")
        initial_screen = create_screen("initial")
        sut = create_sut(initial=initial_screen)
        sut.push(foo_screen)
        foo_screen.reset_mock()
        initial_screen.reset_mock()
        screen_presenter.reset_mock()

        def present(screen: ScreenBase) -> None:
            initial_screen.did_present.assert_not_called()

        screen_presenter.present = Mock(side_effect=present)
        sut.pop(destination="initial")

        screen_presenter.present.assert_called_once()
        initial_screen.did_present.assert_called_once()
